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

from copy import copy

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from django_xmpp_backends import backend

from core.forms import AntiSpamForm
from core.forms import PasswordConfirmationMixin
from core.forms import PasswordMixin

from .formfields import XMPPAccountEmailField
from .formfields import XMPPAccountFingerprintField
from .formfields import XMPPAccountKeyUploadField
from .formfields import XMPPAccountJIDField

User = get_user_model()


class RegistrationForm(AntiSpamForm):
    email = XMPPAccountEmailField()
    if settings.GPG:
        fingerprint = XMPPAccountFingerprintField()
        gpg_key = XMPPAccountKeyUploadField()
    username = XMPPAccountJIDField(register=True, help_text=
        _('At least %(MIN_LENGTH)s and up to %(MAX_LENGTH)s characters. No "@" or spaces.') % {
            'MIN_LENGTH': settings.MIN_USERNAME_LENGTH,
            'MAX_LENGTH': settings.MAX_USERNAME_LENGTH,
        }
    )

    def clean(self):
        data = super(RegistrationForm, self).clean()

        if data.get('username'):  # implies username/domain also present
            if User.objects.filter(jid=data['username']).exists() \
                    or backend.user_exists(username=data['username'], domain=data['domain']):
                self.add_error('username', _("User already exists."))
        return data


class RegistrationConfirmationForm(PasswordConfirmationMixin, AntiSpamForm):
    password = PasswordConfirmationMixin.PASSWORD_FIELD
    password2 = PasswordConfirmationMixin.PASSWORD2_FIELD


class ResetPasswordForm(AntiSpamForm):
    username = XMPPAccountJIDField()


class ResetPasswordConfirmationForm(AntiSpamForm, PasswordConfirmationMixin):
    password = PasswordConfirmationMixin.PASSWORD_FIELD
    password2 = PasswordConfirmationMixin.PASSWORD2_FIELD


class ResetEmailForm(AntiSpamForm, PasswordMixin):
    username = XMPPAccountJIDField()
    email = XMPPAccountEmailField(label=_('New email address'))
    password = PasswordMixin.PASSWORD_FIELD
    if settings.GPG:
        fingerprint = XMPPAccountFingerprintField()
        gpg_key = XMPPAccountKeyUploadField()


class ResetEmailConfirmationForm(AntiSpamForm, PasswordMixin):
    password = PasswordMixin.PASSWORD_FIELD


class DeleteForm(AntiSpamForm, PasswordMixin):
    username = XMPPAccountJIDField()
    password = PasswordMixin.PASSWORD_FIELD


class DeleteConfirmationForm(AntiSpamForm, PasswordMixin):
    password = PasswordMixin.PASSWORD_FIELD
