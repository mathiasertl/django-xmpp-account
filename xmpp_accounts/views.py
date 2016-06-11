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

import json

from datetime import datetime

import pytz

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.generic import View
from django.http import HttpResponse

from core.constants import PURPOSE_SET_PASSWORD
from core.constants import PURPOSE_SET_EMAIL
from core.constants import PURPOSE_DELETE
from core.constants import PURPOSE_REGISTER
from core.constants import REGISTRATION_INBAND
from core.constants import REGISTRATION_WEBSITE
from core.exceptions import RegistrationRateException
from core.views import ConfirmationView
from core.views import ConfirmedView

from .forms import DeleteConfirmationForm
from .forms import DeleteForm
from .forms import RegistrationConfirmationForm
from .forms import RegistrationForm
from .forms import ResetEmailConfirmationForm
from .forms import ResetEmailForm
from .forms import ResetPasswordConfirmationForm
from .forms import ResetPasswordForm

from django_xmpp_backends import backend
from xmpp_backends.base import UserNotFound

User = get_user_model()
tzinfo = pytz.timezone(settings.TIME_ZONE)
_messages = {
    'register': {
        'opengraph_title': _('%(DOMAIN)s: Register a new account'),
        'opengraph_description': _('Register on %(DOMAIN)s, a reliable and secure Jabber server. Jabber is a free and open instant messaging protocol used by millions of people worldwide.'),
    },
    'reset_email': {
        'opengraph_title': _('%(DOMAIN)s: Set a new email address'),
        'opengraph_description': _('Set a new email address for your Jabber account on %(DOMAIN)s. You must have a valid email address set to be able to reset your password.'),
    },
    'reset_password': {
        'opengraph_title': _('%(DOMAIN)s: Reset your password'),
        'opengraph_description': _('Reset the password for your %(DOMAIN)s account.'),
    },
    'delete': {
        'opengraph_title': _('%(DOMAIN)s: Delete your account'),
        'opengraph_description': _('Delete your account on %(DOMAIN)s. WARNING: Once your account is deleted, it can never be restored.'),
    },
}


class RegistrationView(ConfirmationView):
    template_name = 'xmpp_accounts/register/create.html'
    form_class = RegistrationForm

    purpose = PURPOSE_REGISTER
    menuitem = 'register'
    opengraph_title = _messages['register']['opengraph_title']
    opengraph_description = _messages['register']['opengraph_description']

    def registration_rate(self):
        # Check for a registration rate
        cache_key = 'registration-%s' % self.request.get_host()
        registrations = cache.get(cache_key, set())
        _now = datetime.utcnow()

        for key, value in settings.REGISTRATION_RATE.items():
            if len([s for s in registrations if s > _now - key]) >= value:
                raise RegistrationRateException()
        registrations.add(_now)
        cache.set(cache_key, registrations)

    def get_user(self, data):
        last_login = tzinfo.localize(datetime.now())
        return User.objects.create(jid=data['username'], last_login=last_login,
                                   email=data['email'], registration_method=REGISTRATION_WEBSITE)

    def handle_valid(self, form, user):
        domain = user.jid.split('@', 1)[1]
        payload = self.handle_gpg(form, user)
        payload['email'] = form.cleaned_data['email']

        if settings.XMPP_HOSTS[domain].get('RESERVE', False):
            backend.create_reservation(
                username=form.cleaned_data['username'], domain=domain, email=user.email)
        return payload

    def form_valid(self, form):
        self.registration_rate()
        return super(RegistrationView, self).form_valid(form)


class RegistrationConfirmationView(ConfirmedView):
    """Confirm a registration.

    .. NOTE:: This is deliberately not implemented as a generic view related to the Confirmation
       object. We want to present the form unconditionally and complain about a false key only when
       the user passed various Anti-SPAM measures.
    """
    form_class = RegistrationConfirmationForm
    template_name = 'xmpp_accounts/register/confirm.html'
    purpose = PURPOSE_REGISTER
    menuitem = 'register'
    action_url = 'xmpp_accounts:register'
    opengraph_title = _messages['register']['opengraph_title']
    opengraph_description = _messages['register']['opengraph_description']

    def handle_key(self, key, form):
        data = json.loads(key.payload)
        key.user.gpg_fingerprint = data.get('gpg_fingerprint')
        key.user.confirmed = now()
        key.user.save()

        backend.create_user(username=key.user.node, domain=key.user.domain,
                            email=key.user.email, password=form.cleaned_data['password'])
        if settings.WELCOME_MESSAGE is not None:
            reset_pass_path = reverse('xmpp_accounts:reset_password')
            reset_mail_path = reverse('xmpp_accounts:reset_email')
            delete_path = reverse('xmpp_accounts:delete')

            context = {
                'username': key.user.node,
                'domain': key.user.domain,
                'email': key.user.email,
                'password_reset_url': self.request.build_absolute_uri(location=reset_pass_path),
                'email_reset_url': self.request.build_absolute_uri(location=reset_mail_path),
                'delete_url': self.request.build_absolute_uri(location=delete_path),
                'contact_url': self.request.site['CONTACT_URL'],
            }
            subject = settings.WELCOME_MESSAGE['subject'].format(**context)
            message = settings.WELCOME_MESSAGE['message'].format(**context)
            backend.message_user(username=key.user.node, domain=key.user.domain, subject=subject,
                                 message=message)


class ResetPasswordView(ConfirmationView):
    form_class = ResetPasswordForm
#    success_url = reverse_lazy('ResetPasswordThanks')
    template_name = 'xmpp_accounts/reset/password.html'

    purpose = PURPOSE_SET_PASSWORD
    menuitem = 'password'
    opengraph_title = _messages['reset_password']['opengraph_title']
    opengraph_description = _messages['reset_password']['opengraph_description']

    user_not_found_error = _("User not found.")

    def get_user(self, data):
        return User.objects.has_email().get(jid=data['username'])


class ResetPasswordConfirmationView(ConfirmedView):
    form_class = ResetPasswordConfirmationForm
    template_name = 'xmpp_accounts/reset/password-confirm.html'
    purpose = PURPOSE_SET_PASSWORD
    action_url = 'xmpp_accounts:reset_password'
    opengraph_title = _messages['reset_password']['opengraph_title']
    opengraph_description = _messages['reset_password']['opengraph_description']

    def handle_key(self, key, form):
        backend.set_password(username=key.user.node, domain=key.user.domain,
                             password=form.cleaned_data['password'])
        key.user.confirmed = now()
        key.user.save()


class ResetEmailView(ConfirmationView):
    form_class = ResetEmailForm
#    success_url = reverse_lazy('ResetEmailThanks')
    template_name = 'xmpp_accounts/reset/email.html'

    purpose = PURPOSE_SET_EMAIL
    menuitem = 'email'
    opengraph_title = _messages['reset_email']['opengraph_title']
    opengraph_description = _messages['reset_email']['opengraph_description']

    def get_user(self, data):
        """User may or may not exist."""
        jid = data['username']
        node, domain = jid.split('@', 1)
        password = data['password']

        if not backend.check_password(username=node, domain=domain, password=password):
            raise UserNotFound()

        # Defaults are only used for *new* User objects. If they aren't in the database already,
        # it means they registered through InBand-Registration.
        defaults = {
            'email': data['email'],
            'registration_method': REGISTRATION_INBAND,
        }

        user, created = User.objects.get_or_create(jid=jid, defaults=defaults)
        return user

    def handle_valid(self, form, user):
        payload = super(ResetEmailView, self).handle_valid(form, user)
        payload.update(self.handle_gpg(form, user))
        payload['email'] = form.cleaned_data['email']
        return payload


class ResetEmailConfirmationView(ConfirmedView):
    form_class = ResetEmailConfirmationForm
    template_name = 'xmpp_accounts/reset/email-confirm.html'
    purpose = PURPOSE_SET_EMAIL

    action_url = 'xmpp_accounts:reset_email'
    opengraph_title = _messages['reset_email']['opengraph_title']
    opengraph_description = _messages['reset_email']['opengraph_description']

    def handle_key(self, key, form):
        if not backend.check_password(username=key.user.node, domain=key.user.domain,
                                      password=form.cleaned_data['password']):
            raise UserNotFound()

        data = json.loads(key.payload)
        key.user.gpg_fingerprint = data.get('gpg_fingerprint')
        key.user.confirmed = now()

        if 'email' in data:  # set email from payload (might not be present in old keys)
            key.user.email = data['email']

        key.user.save()
        backend.set_email(username=key.user.node, domain=key.user.domain, email=key.user.email)


class DeleteView(ConfirmationView):
    form_class = DeleteForm
    template_name = 'xmpp_accounts/delete/delete.html'

    purpose = PURPOSE_DELETE
    menuitem = 'delete'
    opengraph_title = _messages['delete']['opengraph_title']
    opengraph_description = _messages['delete']['opengraph_description']

    def get_user(self, data):
        try:
            user = User.objects.has_email().get(jid=data['username'])
        except User.DoesNotExist:
            raise UserNotFound()

        node, domain = user.jid.split('@', 1)
        if not backend.check_password(username=node, domain=domain, password=data['password']):
           raise UserNotFound()

        return user


class DeleteConfirmationView(ConfirmedView):
    form_class = DeleteConfirmationForm
    template_name = 'xmpp_accounts/delete/delete-confirm.html'
    purpose = PURPOSE_DELETE
    action_url = 'xmpp_accounts:delete'
    opengraph_title = _messages['delete']['opengraph_title']
    opengraph_description = _messages['delete']['opengraph_description']

    def handle_key(self, key, form):
        username = key.user.node
        domain = key.user.domain
        password = form.cleaned_data['password']

        if not backend.check_password(username=username, domain=domain, password=password):
            raise UserNotFound()

    def after_delete(self, data):
        # actually delete user from the database
        backend.remove_user(username=self.user.node, domain=self.user.domain)
        self.user.delete()


class UserAvailableView(View):
    def post(self, request):
        # Note: XMPP usernames are case insensitive
        username = request.POST.get('username', '').strip().lower()
        domain = request.POST.get('domain', '').strip().lower()
        jid = '%s@%s' % (username, domain)
        print('checking %s' % jid)

        cache_key = 'exists_%s' % jid
        exists = cache.get(cache_key)
        if exists is True:
            return HttpResponse('', status=409)
        elif exists is False:
            return HttpResponse('')

        # Check if the user exists in the database
        if User.objects.filter(jid=jid).exists():
            cache.set(cache_key, True, 30)
            return HttpResponse('', status=409)

        # TODO: Add a setting to rely on the contents of the database and not ask the backend.

        # Check if the user exists in the backend
        if backend.user_exists(username, domain):
            cache.set(cache_key, True, 30)
            return HttpResponse('', status=409)
        else:
            cache.set(cache_key, False, 30)
            return HttpResponse('')
