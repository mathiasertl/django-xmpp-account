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

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from xmppregister.jid import parse_jid

User = get_user_model()

_fieldattrs = {'class': 'form-control', 'maxlength': 30, }
_emailattrs = _fieldattrs.copy()
_emailattrs['type'] = 'email'
_textwidget = forms.TextInput(attrs=_fieldattrs)
_passwidget = forms.PasswordInput(attrs=_fieldattrs)
_mailwidget = forms.TextInput(attrs=_emailattrs)


class PasswordMixin(forms.Form):
    password_error_messages = {
        'password_mismatch': _("The two password fields didn't match.")
    }

    password1 = forms.CharField(label=_("Password"),
                                widget=_passwidget)
    password2 = forms.CharField(label=_("Confirm"),
        widget=_passwidget,
        help_text=_("Enter the same password as above, for verification."))

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.password_error_messages['password_mismatch'])
        return password2


class JidMixin(object):
    USERNAME_FIELD = forms.CharField(
        label=_("Username"), max_length=30, widget=_textwidget,
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")}
    )

    def clean_username(self):
        node = self.cleaned_data.get('username')

        # validate minimum and maximum length
        length = len(node.encode('utf-8'))
        max_length = 1023
        if settings.XMPP_MAX_USERNAME_LENGTH < max_length:
            max_length = settings.XMPP_MAX_USERNAME_LENGTH
        if length > max_length:
            raise forms.ValidationError(_(
                "Username must not be longer then %s characters.") % max_length)
        if length < settings.XMPP_MIN_USERNAME_LENGTH:
            raise forms.ValidationError(_(
                "Username must not be shorter then %s characters.") %
                settings.XMPP_MIN_USERNAME_LENGTH)

        results = parse_jid('%s@example.com' % node)  # fake the server part
        if not results:
            raise forms.ValidationError(_(
                "Username is not a valid XMPP username."))
        return node


class EmailMixin(object):
    EMAIL_FIELD = forms.EmailField(
        max_length=30, widget=_mailwidget,
        help_text=_(
            'Required, a confirmation email will be sent to this address.')
    )


class RegistrationForm(JidMixin, EmailMixin, forms.ModelForm):
    email = EmailMixin.EMAIL_FIELD
    username = JidMixin.USERNAME_FIELD

    class Meta:
        model = User
        fields = ['email', 'username', 'domain']
