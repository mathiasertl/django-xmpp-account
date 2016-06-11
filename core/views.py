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

import logging

from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.six.moves.urllib.parse import urlsplit
from django.utils.translation import ugettext as _
from django.views.generic import FormView
from django.views.generic import View

from brake.decorators import ratelimit

from django_xmpp_backends import backend
from xmpp_backends.base import UserExists
from xmpp_backends.base import UserNotFound

from core.exceptions import GpgError
from core.exceptions import RateException
from core.exceptions import SpamException
from core.models import Address
from core.models import Confirmation
from core.models import UserAddresses
from core.tasks import send_email
from core.utils import confirm
from core.utils import get_client_ip

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
            func = ratelimit(method='POST', rate='15/m')(func)
            ratelimit(method='GET', rate='40/m')(func)(request)

            if getattr(request, 'limited', False):
                raise RateException()

        # We sometimes get requests *without* a user agent. We assume these are automated requests.
        if not request.META.get('HTTP_USER_AGENT'):
            raise SpamException("No user agent passed.")

        return super(AntiSpamFormView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AntiSpamFormView, self).get_context_data(**kwargs)
        context['menuitem'] = getattr(self, 'menuitem', None)

        # Social media
        action_url = self.action_url
        if action_url is not None:
            action_url = reverse(action_url)
        context['ACTION_URL'] = self.request.build_absolute_uri(action_url)
        context['REGISTER_URL'] = self.request.build_absolute_uri('/')

        if 'CANONICAL_HOST' in self.request.site:
            context['ACTION_URL'] = urlsplit(context['ACTION_URL'])._replace(
                netloc=self.request.site['CANONICAL_HOST']).geturl()
            context['REGISTER_URL'] = urlsplit(context['REGISTER_URL'])._replace(
                netloc=self.request.site['CANONICAL_HOST']).geturl()

        context['OPENGRAPH_TITLE'] = self.opengraph_title % self.request.site
        context['OPENGRAPH_DESCRIPTION'] = self.opengraph_description % self.request.site
        context['TWITTER_TEXT'] = getattr(self, 'twitter_text', context['OPENGRAPH_TITLE'])

        form = context['form']
        if settings.GPG and hasattr(form, 'cleaned_data') and 'gpg_key' in form.fields:
            if form['gpg_key'].errors or form['fingerprint'].errors or \
                    form.cleaned_data.get('fingerprint') or form.cleaned_data.get('gpg_key'):
                context['show_gpg'] = True
        return context

    def get_form_kwargs(self):
        kwargs = super(AntiSpamFormView, self).get_form_kwargs()

        if 'domain' in self.form_class.declared_fields:
            kwargs['initial']['domain'] = self.request.site['DOMAIN']
        return kwargs

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class ConfirmationView(AntiSpamFormView):
    user_not_found_error = _("User not found (or false password provided)!")

    def handle_valid(self, form, user):
        """By default, the users current fingerprint is the payload."""

        return {
            'gpg_fingerprint': user.gpg_fingerprint,
            'username': user.node,
            'domain': user.domain,
        }

    def handle_gpg(self, form, user):
        if not settings.GPG:
            return {}  # shortcut

        if form.cleaned_data.get('fingerprint'):
            fingerprint = form.cleaned_data['fingerprint']

            return {'gpg_fingerprint': fingerprint, }
        elif 'gpg_key' in self.request.FILES:
            path = self.request.FILES['gpg_key'].temporary_file_path()
            with open(path) as stream:
                data = stream.read()
            return {'gpg_key': data, }
        else:
            return {'gpg_fingerprint': None, }

    def form_valid(self, form):
        try:
            user = self.get_user(form.cleaned_data)
            payload = self.handle_valid(form, user)
        except GpgError as e:
            form.add_error(e.field, e.message)
            return self.form_invalid(form)
        except User.DoesNotExist:
            form.add_error(None, self.user_not_found_error)
            return self.form_invalid(form)
        except UserNotFound as e:
            if e.args and e.args[0]:
                form.add_error(None, e.args[0].encode('utf-8'))
            else:
                form.add_error(None, self.user_not_found_error)
            return self.form_invalid(form)

        # log user address:
        address = Address.objects.get_or_create(address=self.request.META['REMOTE_ADDR'])[0]
        UserAddresses.objects.create(address=address, user=user, purpose=self.purpose)

        # Send confirmation email to the user
        key, kwargs = confirm(self.request, user, purpose=self.purpose, payload=payload)
        if settings.BROKER_URL is None:
            key.send(**kwargs)
        else:
            send_email.delay(key_id=key.pk, **kwargs)

        return super(ConfirmationView, self).form_valid(form)


class ConfirmedView(AntiSpamFormView):
    user = None

    def dispatch(self, request, *args, **kwargs):
        if request.META.get('HTTP_USER_AGENT', '').startswith('Twitterbot'):
            return HttpResponseRedirect(reverse(self.action_url))
        return super(ConfirmedView, self).dispatch(request, *args, **kwargs)

    def after_delete(self, data):
        pass

    def get_context_data(self, **kwargs):
        context = super(ConfirmedView, self).get_context_data(**kwargs)
        if self.user is not None:
            context['username'] = self.user.node
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
        except UserNotFound as e:
            if e.message:
                form.add_error(None, _("User not found: %s") % e.message)
            else:
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

        cache_key = 'exists_%s@%s' % (username, domain)
        exists = cache.get(cache_key)
        if exists is True:
            return HttpResponse('')
        elif exists is False:
            return HttpResponse('', status=404)

        # Check if the user exists in the database
        try:
            User.objects.get_user(username, domain)
            cache.set(cache_key, True, 30)
            return HttpResponse('')
        except User.DoesNotExist:
            pass

        # Check if the user exists in the backend
        if backend.user_exists(username, domain):
            cache.set(cache_key, True, 30)
            return HttpResponse('')
        else:
            cache.set(cache_key, False, 30)
            return HttpResponse('', status=404)
