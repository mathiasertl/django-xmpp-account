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

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from backends import backend
from backends.base import UserNotFound

from core.constants import PURPOSE_SET_PASSWORD
from core.constants import PURPOSE_SET_EMAIL
from core.constants import REGISTRATION_INBAND
from core.views import ConfirmationView
from core.views import ConfirmedView

from reset.forms import ResetPasswordForm
from reset.forms import ResetPasswordConfirmationForm
from reset.forms import ResetEmailForm
from reset.forms import ResetEmailConfirmationForm

User = get_user_model()

_messages = {
    'email': {
        'opengraph_title': _('%(DOMAIN)s: Set a new email address'),
        'opengraph_description': _('Set a new email address for your Jabber account on %(DOMAIN)s. You must have a valid email address set to be able to reset your password.'),
    },
    'password': {
        'opengraph_title': _('%(DOMAIN)s: Reset your password'),
        'opengraph_description': _('Reset the password for your %(DOMAIN)s account.'),
    },
}


class ResetPasswordView(ConfirmationView):
    form_class = ResetPasswordForm
    success_url = reverse_lazy('ResetPasswordThanks')
    template_name = 'reset/password.html'

    confirm_url_name = 'ResetPasswordConfirmation'
    purpose = PURPOSE_SET_PASSWORD
    email_subject = _('Reset the password for your %(domain)s account')
    email_template = 'reset/password-mail'
    menuitem = 'password'
    opengraph_title = _messages['password']['opengraph_title']
    opengraph_description = _messages['password']['opengraph_description']

    user_not_found_error = _("User not found.")

    def get_user(self, data):
        user = User.objects.get(username=data['username'], domain=data['domain'])
        user.has_email()
        return user


class ResetPasswordConfirmationView(ConfirmedView):
    form_class = ResetPasswordConfirmationForm
    template_name = 'reset/password-confirm.html'
    purpose = PURPOSE_SET_PASSWORD
    action_url = 'ResetPassword'
    opengraph_title = _messages['password']['opengraph_title']
    opengraph_description = _messages['password']['opengraph_description']

    def handle_key(self, key, form):
        backend.set_password(username=key.user.username, domain=key.user.domain,
                             password=form.cleaned_data['password'])
        key.user.confirmed = now()
        key.user.save()


class ResetEmailView(ConfirmationView):
    form_class = ResetEmailForm
    success_url = reverse_lazy('ResetEmailThanks')
    template_name = 'reset/email.html'

    confirm_url_name = 'ResetEmailConfirmation'
    purpose = PURPOSE_SET_EMAIL
    email_subject = _('Confirm the email address for your %(domain)s account')
    email_template = 'reset/email-mail'
    menuitem = 'email'
    opengraph_title = _messages['email']['opengraph_title']
    opengraph_description = _messages['email']['opengraph_description']

    def get_user(self, data):
        """User may or may not exist."""
        username = data['username']
        domain = data['domain']
        password = data['password']

        if not backend.check_password(username=username, domain=domain, password=password):
            raise UserNotFound()

        # Defaults are only used for *new* User objects. If they aren't in the database already,
        # it means they registered through InBand-Registration.
        defaults = {
            'email': data['email'],
            'registration_method': REGISTRATION_INBAND,
        }

        user, created = User.objects.get_or_create(username=username, domain=domain,
                                                   defaults=defaults)

        if not created:
            user.email = data['email']
            user.confirmed = None
            user.save()

        return user

    def handle_valid(self, form, user):
        payload = super(ResetPasswordView, self).handle_valid(form, user)
        payload.update(self.handle_gpg(form, user))
        payload['email'] = form.cleaned_data['email']
        return payload


class ResetEmailConfirmationView(ConfirmedView):
    form_class = ResetEmailConfirmationForm
    template_name = 'reset/email-confirm.html'
    purpose = PURPOSE_SET_EMAIL

    action_url = 'ResetEmail'
    opengraph_title = _messages['email']['opengraph_title']
    opengraph_description = _messages['email']['opengraph_description']

    def handle_key(self, key, form):
        if not backend.check_password(username=key.user.username, domain=key.user.domain,
                                      password=form.cleaned_data['password']):
            raise UserNotFound()

        data = json.loads(key.payload)
        key.user.gpg_fingerprint = data.get('gpg_fingerprint')
        key.user.confirmed = now()
        key.user.save()
        backend.set_email(username=key.user.username, domain=key.user.domain, email=key.user.email)
