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

from __future__ import unicode_literals, absolute_import

from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model

from brake.decorators import ratelimit
from xmpp_backends.base import UserExists
from xmpp_backends.base import UserNotFound

from core.exceptions import RateException
from core.exceptions import SpamException
from core.models import Address
from core.models import Confirmation
from core.models import UserAddresses
from core.tasks import send_email
from core.utils import confirm
from core.utils import get_client_ip

User = get_user_model()


class AntiSpamMixin(object):
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

        return super(AntiSpamMixin, self).dispatch(request, *args, **kwargs)


class ConfirmationMixin(object):
    # TODO: Very ugly here (should be part of the form or so)
    user_not_found_error = _("User not found (or false password provided)!")

    def get_template_names(self):
        return ['xmpp_accounts/%s/main.html' % self.purpose]

    def gpg_from_form(self, form):
        if not settings.GPG:
            return {}  # shortcut

        if form.cleaned_data.get('fingerprint'):
            return {'gpg_encrypt': form.cleaned_data.get('fingerprint'), }
        elif 'gpg_key' in self.request.FILES:
            path = self.request.FILES['gpg_key'].temporary_file_path()
            with open(path) as stream:
                data = stream.read()
            return {'gpg_key': data, }
        return {}

    def gpg_from_user(self, user):
        if not settings.GPG or not user.gpg_fingerprint:
            return {}
        return {'gpg_encrypt': user.gpg_fingerprint}

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

        # log user address:
        address = Address.objects.get_or_create(address=self.request.META['REMOTE_ADDR'])[0]
        # TODO: this is still an int in the db
        UserAddresses.objects.create(address=address, user=user, purpose=self.purpose)

        # Send confirmation email to the user
        key, kwargs = confirm(self.request, user, purpose=self.purpose, payload=payload)
        if settings.BROKER_URL is None:
            key.send(**kwargs)
        else:
            send_email.delay(key_id=key.pk, **kwargs)

        return super(ConfirmationMixin, self).form_valid(form)


class ConfirmedMixin(object):
    user = None

    def get_template_names(self):
        return ['xmpp_accounts/%s/confirm.html' % self.purpose]

    def dispatch(self, request, *args, **kwargs):
        if request.META.get('HTTP_USER_AGENT', '').startswith('Twitterbot'):
            return HttpResponseRedirect(reverse('xmpp_accounts:%s' % self.purpose))
        return super(ConfirmedMixin, self).dispatch(request, *args, **kwargs)

    def after_delete(self, user, form):
        pass

    def get_context_data(self, **kwargs):
        context = super(ConfirmedMixin, self).get_context_data(**kwargs)
        if self.user is not None:
            context['username'] = self.user.node
            context['domain'] = self.user.domain
            context['jid'] = self.user.jid
        return context

    def form_valid(self, form):
        try:
            key = Confirmation.objects.valid().purpose(self.purpose).get(key=self.kwargs['key'])
        except Confirmation.DoesNotExist:
            form.add_error(None, _("Confirmation key expired or not found."))
            return self.form_invalid(form)
        self.user = User.objects.get(jid=key.payload['extra']['jid'])

        try:
            self.handle_key(key, self.user, form)
            key.delete()
            self.after_delete(self.user, form)
        except UserNotFound as e:
            if e.message:
                form.add_error(None, _("User not found: %s") % e.message)
            else:
                form.add_error(None, _("User not found!"))
            return self.form_invalid(form)
        except UserExists:
            form.add_error(None, _("User already exists!"))
            return self.form_invalid(form)

        return super(ConfirmedMixin, self).form_valid(form)
