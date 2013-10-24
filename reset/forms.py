# -*- coding: utf-8 -*-
#
# This file is part of xmppregister (https://account.jabber.at/doc).
#
# xmppregister is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmppregister is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xmppregister.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django.contrib.auth import get_user_model

from core.forms import AntiSpamForm
from core.forms import AntiSpamModelForm
from core.forms import EmailMixin
from core.forms import JidMixin
from core.forms import PasswordMixin

User = get_user_model()


class ResetPasswordForm(AntiSpamModelForm, JidMixin, EmailMixin):
    email = EmailMixin.EMAIL_FIELD
    username = JidMixin.USERNAME_FIELD

    class Meta:
        model = User
        fields = ['email', 'username', 'domain']


class ResetPasswordConfirmationForm(AntiSpamForm, PasswordMixin):
    password1 = PasswordMixin.PASSWORD1
    password2 = PasswordMixin.PASSWORD2


class ResetEmailForm(AntiSpamModelForm, JidMixin, PasswordMixin):
    username = JidMixin.USERNAME_FIELD
    password1 = PasswordMixin.PASSWORD1
    password2 = PasswordMixin.PASSWORD2

    class Meta:
        model = User
        fields = ['username', 'domain']


class ResetEmailConfirmationForm(AntiSpamForm, EmailMixin):
    email = EmailMixin.EMAIL_FIELD