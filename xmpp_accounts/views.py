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

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from core.constants import PURPOSE_SET_PASSWORD
from core.constants import PURPOSE_SET_EMAIL
from core.constants import PURPOSE_DELETE
from core.constants import REGISTRATION_INBAND
from core.views import ConfirmationView
from core.views import ConfirmedView

from .forms import DeleteForm
from .forms import DeleteConfirmationForm
from .forms import ResetPasswordForm
from .forms import ResetPasswordConfirmationForm
from .forms import ResetEmailForm
from .forms import ResetEmailConfirmationForm

from django_xmpp_backends import backend
from xmpp_backends.base import UserNotFound

User = get_user_model()
_messages = {
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
        return User.objects.has_email().get_user(username=data['username'], domain=data['domain'])


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
        username = data['username']
        domain = data['domain']
        jid = '%s@%s' % (data['username'], data['domain'])
        password = data['password']

        if not backend.check_password(username=username, domain=domain, password=password):
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
        username = data['username']
        domain = data['domain']

        try:
            user = User.objects.has_email().get_user(username, domain)
        except User.DoesNotExist:
            raise UserNotFound()

        if not backend.check_password(username=username, domain=domain, password=data['password']):
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
