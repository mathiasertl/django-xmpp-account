# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:hlsearch
#
# This file is part of django-xmpp-account (https://github.com/mathiasertl/django-xmpp-account/).
#
# django-xmpp-account is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# django-xmpp-account is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with django-xmpp-account.
# If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import six
from django.utils.six.moves.urllib.parse import urlsplit
from django.utils.translation import ugettext as _
from django.views.generic import FormView
from django.views.generic import View

from brake.decorators import ratelimit

from recaptcha import RecaptchaUnreachableError

from backends import backend
from backends.base import UserExists
from backends.base import UserNotFound

from core.exceptions import RateException
from core.exceptions import TemporaryError
from core.models import Address
from core.models import Confirmation
from core.models import UserAddresses
from core.utils import get_client_ip
from core.utils import gpg_lock

User = get_user_model()
log = logging.getLogger(__name__)


class AntiSpamFormView(FormView):
    action_url = None

    def dispatch(self, request, *args, **kwargs):
        remote_ip = get_client_ip(request)

        if settings.DEBUG is False and remote_ip not in settings.RATELIMIT_WHITELIST:
            # create a dummy function and dynamically set its name. This way,
            # the ratelimit decorator is specific to the method in each class.
            def func(request):
                pass
            func.__name__ = str('%s_dispatch' % self.__class__.__name__)
            func = ratelimit(method='POST', rate='10/m')(func)
            ratelimit(method='GET', rate='30/m')(func)(request)

            if getattr(request, 'limited', False):
                raise RateException()

        try:
            if settings.RECAPTCHA_CLIENT is not None and request.method == 'POST':
                try:
                    if six.PY3:
                        request.POST['recaptcha_response_field'].encode(settings.DEFAULT_CHARSET)
                    else:
                        request.POST['recaptcha_response_field'].decode(settings.DEFAULT_CHARSET)
                except UnicodeEncodeError:
                    raise TemporaryError(_("Your CAPTCHA response contained invalid characters."))

            return super(AntiSpamFormView, self).dispatch(request, *args, **kwargs)
        except RecaptchaUnreachableError:
            raise TemporaryError(_("The ReCAPTCHA server was unreacheable."))
#        except KeyError:
#            raise TemporaryError(_("The ReCAPTCHA didn't work properly."))

    def get_context_data(self, **kwargs):
        context = super(AntiSpamFormView, self).get_context_data(**kwargs)
        context['menuitem'] = getattr(self, 'menuitem', None)

        # Social media
        action_url = self.action_url
        if action_url is not None:
            action_url = reverse(action_url)
        context['ACTION_URL'] = self.request.build_absolute_uri(action_url)

        if 'CANONICAL_HOST' in self.request.site:
            context['ACTION_URL'] = urlsplit(context['ACTION_URL'])._replace(
                netloc=self.request.site['CANONICAL_HOST']).geturl()

        context['OPENGRAPH_TITLE'] = self.opengraph_title % self.request.site
        context['OPENGRAPH_DESCRIPTION'] = self.opengraph_description % self.request.site
        context['TWITTER_TEXT'] = getattr(self, 'twitter_text', context['OPENGRAPH_TITLE'])

        form = context['form']
        if hasattr(form, 'cleaned_data'):
            if 'fingerprint' in form.cleaned_data or 'gpg_key' in form.cleaned_data:
                context['show_gpg'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(AntiSpamFormView, self).get_form_kwargs()
        if settings.RECAPTCHA_CLIENT is not None:
            kwargs['request'] = self.request

        if 'domain' in self.form_class.declared_fields:
            kwargs['initial']['domain'] = self.request.site['DOMAIN']
        return kwargs

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ConfirmationView(AntiSpamFormView):
    """
    Keys:

    * confirm_url_name
    * email_subject
    * email_template
    * purpose
    """
    user_not_found_error = _("User not found (or false password provided)!")

    def handle_valid(self, form, user):
        """By default, the users current fingerprint is the payload."""

        return {
            'gpg_fingerprint': user.gpg_fingerprint,
            'username': user.username,
            'domain': user.domain,
        }

    def handle_gpg(self, form, user):
        if not settings.GPG:
            return  # shortcut

        if form.cleaned_data.get('fingerprint'):
            fingerprint = form.cleaned_data['fingerprint']
            with gpg_lock:
                imported = settings.GPG.recv_keys(settings.GPG_KEYSERVER, fingerprint)
            if not imported.fingerprints:
                raise Exception("No imported keys: %s (fp: '%s')" % (imported.stderr, fingerprint))
            return {'gpg_fingerprint': fingerprint, }
        elif 'gpg_key' in self.request.FILES:
            path = self.request.FILES['gpg_key'].temporary_file_path()
            with open(path) as stream, gpg_lock:
                data = stream.read()
            imported = settings.GPG.import_keys(data)
            if not imported.fingerprints:
                raise Exception("No imported keys: %s\ndata: %s" % (imported.stderr, data))
            return {'gpg_fingerprint': imported.fingerprints[0], }
        else:
            return {'gpg_fingerprint': None, }

    def form_valid(self, form):
        try:
            user = self.get_user(form.cleaned_data)
            payload = self.handle_valid(form, user)
        except User.DoesNotExist:
            form.add_error(None, self.user_not_found_error)
            return self.form_invalid(form)
        except UserNotFound as e:
            if e.args and e.args[0]:
                form.add_error(None, e.args[0].encode('utf-8'))
            else:
                form.add_error(None, self.user_not_found_error)
            return self.form_invalid(form)
        except (IntegrityError, UserExists) as e:
            form.add_error(None, _("User already exists.") + str(e))
            return self.form_invalid(form)

        payload = json.dumps(payload)

        # log user address:
        address = Address.objects.get_or_create(address=self.request.META['REMOTE_ADDR'])[0]
        UserAddresses.objects.create(address=address, user=user, purpose=self.purpose)

        # create a confirmation key before returning the response
        key = Confirmation.objects.create(user=user, purpose=self.purpose, payload=payload)
        key.send(
            request=self.request, template_base=self.email_template,
            subject=self.email_subject % {'domain': user.domain, },
            confirm_url_name=self.confirm_url_name
        )

        return super(ConfirmationView, self).form_valid(form)


class ConfirmedView(AntiSpamFormView):
    user = None

    def dispatch(self, request, *args, **kwargs):
        if request.META['HTTP_USER_AGENT'].startswith('Twitterbot'):
            return HttpResponseRedirect(reverse(self.action_url))
        return super(ConfirmedView, self).dispatch(request, *args, **kwargs)

    def after_delete(self, data):
        pass

    def get_context_data(self, **kwargs):
        context = super(ConfirmedView, self).get_context_data(**kwargs)
        if self.user is not None:
            context['username'] = self.user.username
            context['domain'] = self.user.domain
            context['jid'] = self.user.jid
        return context

    def form_valid(self, form):
        try:
            key = Confirmation.objects.valid().filter(
                purpose=self.purpose).get(key=self.kwargs['key'])
        except Confirmation.DoesNotExist:
            form.add_error(None, _("Confirmation key expired or not found."))
            return self.form_invalid(form)
        self.user = key.user

        try:
            self.handle_key(key, form)
            key.delete()
            self.after_delete(form.cleaned_data)
        except UserNotFound:
            form.add_error(None, _("User not found!"))
            return self.form_invalid(form)
        except UserExists:
            form.add_error(None, _("User already exists!"))
            return self.form_invalid(form)

        return super(ConfirmedView, self).form_valid(form)


class ExistsView(View):
    def post(self, request):
        username = request.POST.get('username', '').strip().lower()
        domain = request.POST.get('domain', '').strip().lower()
        log.info('Checking %s@%s for existence.', username, domain)

        # Check if the user exists in the database
        try:
            User.objects.get_user(username, domain)
            print('exists in db')
            return HttpResponse('')
        except User.DoesNotExist:
            pass

        # Check if the user exists in the backend
        if backend.exists(username, domain):
            print('exists in backend')
            return HttpResponse('')
        else:
            return HttpResponse('', status=404)
