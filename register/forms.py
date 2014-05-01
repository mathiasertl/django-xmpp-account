# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-register (https://account.jabber.at/doc).
#
# django-xmpp-register is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# django-xmpp-register is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# django-xmpp-register.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from copy import copy

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from core.forms import AntiSpamForm
from core.forms import EmailBlockedMixin
from core.forms import JidMixin
from core.forms import PasswordConfirmationMixin

User = get_user_model()


class RegistrationForm(JidMixin, EmailBlockedMixin, AntiSpamForm):
    email = EmailBlockedMixin.EMAIL_FIELD
    username = copy(JidMixin.USERNAME_FIELD)  # copy because we override some fields
    domain = JidMixin.DOMAIN_FIELD

    username.help_text = _(
        'At least %(MIN_LENGTH)s and up to %(MAX_LENGTH)s characters. No "@" or spaces.')


class RegistrationConfirmationForm(PasswordConfirmationMixin, AntiSpamForm):
    password = PasswordConfirmationMixin.PASSWORD_FIELD
    password2 = PasswordConfirmationMixin.PASSWORD2_FIELD
