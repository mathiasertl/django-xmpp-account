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
import time

from copy import copy

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string
from django.utils.crypto import salted_hmac
from django.utils.translation import ugettext_lazy as _

from captcha.fields import CaptchaField

from xmppaccount.jid import parse_jid

from core.exceptions import SpamException
from core.exceptions import RateException
from core.widgets import PasswordWidget
from core.widgets import SelectWidget
from core.widgets import TextWidget

log = logging.getLogger(__name__)

class UserCreationFormNoPassword(UserCreationForm):
    #TODO: Dead code?
    def __init__(self, *args, **kwargs):
        super(UserCreationFormNoPassword, self).__init__(*args, **kwargs)
        del self.fields['password1']
        del self.fields['password2']


class AntiSpamForm(forms.Form):
    timestamp = forms.IntegerField(widget=forms.HiddenInput, required=True)
    token = forms.CharField(widget=forms.HiddenInput, required=True)
    security_hash = forms.CharField(required=True, widget=forms.HiddenInput)

    if settings.ENABLE_CAPTCHAS:
        captcha = CaptchaField(help_text=_(
            'This <a href="https://en.wikipedia.org/wiki/CAPTCHA">CAPTCHA</a> prevents '
            'automated SPAM. If you can\'t read it, just <a '
            'class="js-captcha-refresh">&#8634; reload</a> it.'
        ))

    ANTI_SPAM_MESSAGES = {
        'too-slow': _("This page has expired. Reload and try again."),
    }

    def __init__(self, *args, **kwargs):
        kwargs['initial'] = self.init_security(kwargs.get('initial', {}))
        super(AntiSpamForm, self).__init__(*args, **kwargs)

    def generate_hash(self, timestamp, token):
        key_salt = 'xmppaccount.core.forms.AntiSpamFormBase'
        value = '%s-%s' % (timestamp, token)
        return salted_hmac(key_salt, value).hexdigest()

    def init_security(self, initial):
        initial['timestamp'] = int(time.time())
        initial['token'] = get_random_string(32)
        initial['security_hash'] = self.generate_hash(initial['timestamp'], initial['token'])
        return initial

    def clean(self):
        data = super(AntiSpamForm, self).clean()
        if isinstance(self, JidMixin) and data.get('username') and data.get('domain'):
            data['jid'] = '%s@%s' % (data['username'], data['domain'])
        return data

    def clean_timestamp(self):
        now = time.time()
        timestamp = self.cleaned_data.get("timestamp")
        if timestamp is None:
            raise SpamException(_("Missing form-field."))

        if now - 1 < timestamp:  # MUCH to fast - definetly spam
            raise SpamException(_("Form submitted within one second."))
        elif now - 3 < timestamp:  # submit is to fast.
            raise RateException()
        elif now - (settings.FORM_TIMEOUT) > timestamp:
            raise forms.ValidationError(self.ANTI_SPAM_MESSAGES['too-slow'])
        return timestamp

    def clean_security_hash(self):
        good = self.generate_hash(self.data.get("timestamp", ''), self.data.get("token", ''))
        received = self.cleaned_data.get('security_hash')
        if received is None:
            raise SpamException(_("No security hash"))
        if received != good:
            raise SpamException(_("Wrong security hash"))
        return received

    def clean_value(self):
        value = self.cleaned_data["value"]

        if value:
            raise SpamException(_("Wrong value: \"%s\"") % value)
        return value


class PasswordMixin(object):
    PASSWORD_FIELD = forms.CharField(label=_("Password"), max_length=60, widget=PasswordWidget)


class PasswordConfirmationMixin(PasswordMixin):
    password_error_messages = {
        'password_mismatch': _("The two password fields didn't match.")
    }

    PASSWORD2_FIELD = forms.CharField(
        label=_("Confirm"), widget=PasswordWidget, max_length=60,
        help_text=_("Enter the same password as above, for verification."))

    def clean_password2(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(self.password_error_messages['password_mismatch'])
        return password2


class JidMixin(object):
    USERNAME_FIELD = forms.CharField(label=_("Username"), max_length=settings.MAX_USERNAME_LENGTH,
                                     widget=TextWidget)

    DOMAIN_FIELD = forms.ChoiceField(
        widget=SelectWidget,
        initial=settings.DEFAULT_XMPP_HOST,
        choices=tuple([(d, '@%s' % d) for d in settings.REGISTRATION_HOSTS])
    )
    ALL_DOMAINS_FIELD = forms.ChoiceField(
        widget=copy(SelectWidget),
        initial=settings.DEFAULT_XMPP_HOST,
        choices=tuple([(d, '@%s' % d) for d in settings.MANAGED_HOSTS])
    )

    def clean_domain(self):
        domain = self.cleaned_data.get('domain', '').lower().strip()
        if domain not in settings.XMPP_HOSTS:
            raise forms.ValidationError(_('Unknown domain given'))
        return domain

    def clean_username(self):
        node = self.cleaned_data.get('username', '').lower().strip()

        # validate minimum and maximum length
        length = len(node.encode('utf-8'))
        max_length = min(settings.MAX_USERNAME_LENGTH, 1023)
        self._username_status = 'ok'

        if length > max_length:
            self._username_status = 'too-long'
            raise forms.ValidationError(
                _("Username must not be longer then %s characters.") % max_length)
        if length < settings.MIN_USERNAME_LENGTH:
            self._username_status = 'too-short'
            raise forms.ValidationError(_(
                "Username must not be shorter then %s characters.") % settings.MIN_USERNAME_LENGTH)

        results = parse_jid('%s@example.com' % node)  # fake the server part
        if not results:
            self._username_status = 'invalid'
            raise forms.ValidationError(_("Username is not a valid XMPP username."))
        return node


class EmailMixin(object):
    GPG_KEY_FIELD = forms.FileField(
        required=False,
        help_text=_('Upload your ASCII armored GPG key directly ("gpg --armor --export <fingerprint>").')
    )

    def clean_gpg_key(self):
        if not settings.GPG: # check, just to be sure
            raise forms.ValidationError('GPG not enabled.')

        gpg_key = self.cleaned_data.get('gpg_key')
        if gpg_key is None:
            return gpg_key
        if gpg_key.content_type not in ['text/plain', 'application/pgp-encrypted']:
            raise forms.ValidationError(
                'Only plain-text files are allowed (was: %s)!' % gpg_key.content_type)

        result = settings.GPG.scan_keys(gpg_key.temporary_file_path())
        if result.stderr:
            log.error('Could not import public key: %s', result.stderr)
            raise forms.ValidationError('Could not import public key.')
        elif len(result.fingerprints) > 1:
            raise forms.ValidationError(_('File contains multiple keys.'))
        elif len(result.fingerprints) < 1:
            raise forms.ValidationError(_('File contains no keys.'))

        return gpg_key
