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

from backends import backend
from core.forms import AntiSpamForm
from core.forms import EmailBlockedMixin
from core.forms import JidMixin
from core.forms import PasswordConfirmationMixin

User = get_user_model()


class RegistrationForm(JidMixin, EmailBlockedMixin, AntiSpamForm):
    email = EmailBlockedMixin.EMAIL_FIELD
    if settings.GPG:
        fingerprint = EmailBlockedMixin.FINGERPRINT_FIELD
        gpg_key = EmailBlockedMixin.GPG_KEY_FIELD
    username = copy(JidMixin.USERNAME_FIELD)  # copy because we override some fields
    domain = JidMixin.DOMAIN_FIELD

    username.help_text = _(
        'At least %(MIN_LENGTH)s and up to %(MAX_LENGTH)s characters. No "@" or spaces.')


    def clean(self):
        data = super(RegistrationForm, self).clean()
        if data.get('jid'):  # implies username/domain also present
            if User.objects.filter(jid=data['jid']).exists() \
                    or backend.user_exists(username=data['username'], domain=data['domain']):
                self._username_status = 'taken'
                raise forms.ValidationError(_("User already exists."))
        return data


class RegistrationConfirmationForm(PasswordConfirmationMixin, AntiSpamForm):
    password = PasswordConfirmationMixin.PASSWORD_FIELD
    password2 = PasswordConfirmationMixin.PASSWORD2_FIELD
