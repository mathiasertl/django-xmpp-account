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

import time

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.crypto import salted_hmac

from django_recaptcha_field import create_form_subclass_with_recaptcha

from core.exceptions import SpamException
from core.exceptions import RateException
from core.utils import random_string


class AntiSpamBase(object):
    VALUE = forms.CharField(required=False)
    TIMESTAMP = forms.IntegerField(widget=forms.HiddenInput)
    TOKEN = forms.CharField(widget=forms.HiddenInput)
    SECURITY_HASH = forms.CharField(min_length=40, max_length=40, widget=forms.HiddenInput)

    ANTI_SPAM_MESSAGES = {
        'too-slow': _("We're sorry, but your session was lost. Please reload this page and try again."),
    }

    def generate_hash(self, timestamp, token):
        key_salt = 'xmppregister.core.forms.AntiSpamBase'
        value = '%s-%s' % (timestamp, token)
        return salted_hmac(key_salt, value).hexdigest()

    def init_security(self, initial):
        initial['timestamp'] = int(time.time())
        initial['token'] = random_string()
        initial['security_hash'] = self.generate_hash(initial['timestamp'],
                                                      initial['token'])
        return initial

    def clean_timestamp(self):
        now = time.time()
        timestamp = self.cleaned_data["timestamp"]

        if now - 1 < timestamp:  # MUCH to fast - definetly spam
            raise SpamException()
        elif now - 3 < timestamp:  # submit is to fast.
            raise RateException()
        elif now - (settings.FORM_TIMEOUT) > timestamp:
            raise forms.ValidationError(self.ANTI_SPAM_MESSAGES['too-slow'])
        return self.cleaned_data["timestamp"]

    def clean_security_hash(self):
        good = self.generate_hash(self.cleaned_data["timestamp"],
                                  self.cleaned_data["token"])
        received = self.cleaned_data['security_hash']
        if received != good:
            raise SpamException()
        return received

    def clean_value(self):
        value = self.cleaned_data["value"]

        if value:
            raise SpamException()
        return value

class AntiSpamBaseForm(forms.Form, AntiSpamBase):
    value = AntiSpamBase.VALUE
    timestamp = AntiSpamBase.TIMESTAMP
    token = AntiSpamBase.TOKEN
    security_hash = AntiSpamBase.SECURITY_HASH

    def __init__(self, *args, **kwargs):
        kwargs['initial'] = self.init_security(kwargs.get('initial', {}))
        super(AntiSpamBaseForm, self).__init__(*args, **kwargs)


class AntiSpamModelBaseForm(forms.ModelForm, AntiSpamBase):
    value = AntiSpamBase.VALUE
    timestamp = AntiSpamBase.TIMESTAMP
    token = AntiSpamBase.TOKEN
    security_hash = AntiSpamBase.SECURITY_HASH

    def __init__(self, *args, **kwargs):
        kwargs['initial'] = self.init_security(kwargs.get('initial', {}))
        super(AntiSpamModelBaseForm, self).__init__(*args, **kwargs)

if settings.RECAPTCHA_CLIENT is not None:
    AntiSpamModelForm = create_form_subclass_with_recaptcha(
        AntiSpamModelBaseForm, settings.RECAPTCHA_CLIENT)
    AntiSpamForm = create_form_subclass_with_recaptcha(
        AntiSpamBaseForm, settings.RECAPTCHA_CLIENT)
else:
    AntiSpamModelForm = AntiSpamModelBaseForm
    AntiSpamForm = AntiSpamBaseForm
