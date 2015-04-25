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
import re
import time

from copy import copy

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import salted_hmac

from django_recaptcha_field import _RecaptchaField

from xmppaccount.jid import parse_jid

from core.exceptions import SpamException
from core.exceptions import RateException
from core.utils import random_string
from core.widgets import EmailWidget
from core.widgets import FingerprintWidget
from core.widgets import PasswordWidget
from core.widgets import SelectWidget
from core.widgets import TextWidget

log = logging.getLogger(__name__)

def create_form_subclass_with_recaptcha(base_form_class, recaptcha_client,
                                        additional_field_kwargs=None):
    """Copy from django_recaptcha_field.py overriding the class used for the recaptcha field."""

    additional_field_kwargs = additional_field_kwargs or {}

    class RecaptchaProtectedForm(base_form_class):

        def __init__(self, request, *args, **kwargs):
            super(RecaptchaProtectedForm, self).__init__(*args, **kwargs)

            self.fields['recaptcha'] = RecaptchaField(
                recaptcha_client,
                request.META['REMOTE_ADDR'],
                request.is_secure(),
                **additional_field_kwargs
                )

    return RecaptchaProtectedForm


class RecaptchaField(_RecaptchaField):
    """Subclass adding the missing error message."""

    default_error_messages = {
        'incorrect_solution': 'Your solution to the CAPTCHA was incorrect',
        # This key is missing upstream, which sometimes causes tracebacks
        'invalid': 'This field is invalid.',
    }


class UserCreationFormNoPassword(UserCreationForm):
    #TODO: Dead code?
    def __init__(self, *args, **kwargs):
        super(UserCreationFormNoPassword, self).__init__(*args, **kwargs)
        del self.fields['password1']
        del self.fields['password2']


class AntiSpamFormBase(forms.Form):
    timestamp = forms.IntegerField(widget=forms.HiddenInput, required=True)
    token = forms.CharField(widget=forms.HiddenInput, required=True)
    security_hash = forms.CharField(required=True, widget=forms.HiddenInput)

    ANTI_SPAM_MESSAGES = {
        'too-slow': _("This page has expired. Reload and try again."),
    }

    def __init__(self, *args, **kwargs):
        kwargs['initial'] = self.init_security(kwargs.get('initial', {}))
        super(AntiSpamFormBase, self).__init__(*args, **kwargs)

    def generate_hash(self, timestamp, token):
        key_salt = 'xmppaccount.core.forms.AntiSpamFormBase'
        value = '%s-%s' % (timestamp, token)
        return salted_hmac(key_salt, value).hexdigest()

    def init_security(self, initial):
        initial['timestamp'] = int(time.time())
        initial['token'] = random_string()
        initial['security_hash'] = self.generate_hash(initial['timestamp'], initial['token'])
        return initial

    def clean(self):
        data = super(AntiSpamFormBase, self).clean()
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
        domain = self.cleaned_data.get('domain')
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
    EMAIL_FIELD = forms.EmailField(
        label=_("email"), max_length=50, widget=EmailWidget,
        help_text=_('Required, a confirmation email will be sent to this address.')
    )
    FINGERPRINT_FIELD = forms.CharField(
        label=_('GPG key (advanced, optional)'), max_length=50, required=False,
        widget=FingerprintWidget,
        help_text=_(
            'Add your fingerprint ("gpg --list-secret-keys --fingerprint") if your key is '
            'available on the public key servers.')
    )
    GPG_KEY_FIELD = forms.FileField(
        required=False,
        help_text=_('Upload your ASCII armored GPG key directly ("gpg --armor --export <fingerprint>").')
    )
    EMAIL_ERROR_MESSAGES = {
        'own-domain': _(
            "This Jabber host does not provide email addresses. You're supposed to give your own "
            "email address."
        ),
        'blocked-domain': _(
            "Email addresses with this domain are blocked and cannot be used on this site."
        ),
    }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        try:
            hostname = email.rsplit('@', 1)[1]
            if hostname in settings.NO_EMAIL_HOSTS:
                raise forms.ValidationError(
                    self.EMAIL_ERROR_MESSAGES['own-domain'])
        except IndexError:
            pass
        return email

    def clean_fingerprint(self):
        fp = self.cleaned_data.get('fingerprint', '').strip().replace(' ', '').upper()
        if fp == '':
            return None  # no fingerprint given
        if len(fp) != 40:
            raise forms.ValidationError(_("Fingerprint should be 40 characters long."))
        if re.search('[^A-F0-9]', fp) is not None:
            raise forms.ValidationError(_("Fingerprint contains invalid characters."))

        # actually search for the key
        keys = settings.GPG.search_keys(fp, settings.GPG_KEYSERVER)
        if len(keys) > 1:
            raise forms.ValidationError(_("Multiple keys with that fingerprint found."))
        elif len(keys) < 1:
            raise forms.ValidationError(_("No key with that fingerprint found."))
        return fp

    def clean_gpg_key(self):
        gpg_key = self.cleaned_data.get('gpg_key')
        if gpg_key is None:
            return gpg_key
        if gpg_key.content_type != 'text/plain':
            raise forms.ValidationError(
                'Only plain-text files are allowed (was: %s)!' % gpg_key.content_type)

        if settings.GPG:  # check, just to be sure
            result = settings.GPG.scan_keys(gpg_key.temporary_file_path())
            if result.stderr:
                log.error('Could not import public key: %s', result.stderr)
                raise forms.ValidationError('Could not import public key.')
            elif len(result.fingerprints) > 1:
                raise forms.ValidationError(_('File contains multiple keys.'))
            elif len(result.fingerprints) < 1:
                raise forms.ValidationError(_('File contains no keys.'))
        else:
            raise forms.ValidationError('GPG not enabled.')

        return gpg_key


class EmailBlockedMixin(EmailMixin):
    def clean_email(self):
        email = super(EmailBlockedMixin, self).clean_email()
        try:
            hostname = email.rsplit('@', 1)[1]
            if hostname in settings.BLOCKED_EMAIL_TLDS:
                raise forms.ValidationError(self.EMAIL_ERROR_MESSAGES['blocked-domain'])
        except IndexError:
            pass
        return email


# dynamically make BaseForms to CAPTCHA forms if settings.RECAPTCHA_CLIENT
if settings.RECAPTCHA_CLIENT is not None:
    AntiSpamForm = create_form_subclass_with_recaptcha(AntiSpamFormBase, settings.RECAPTCHA_CLIENT)
else:
    # WARNING: Do not rename form class to "AntiSpamForm" and skip this branch: The constructor
    # would raise "maximum recursion depth exceeded"
    AntiSpamForm = AntiSpamFormBase
