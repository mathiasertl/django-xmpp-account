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

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from captcha.fields import CaptchaField


class AntiSpamForm(forms.Form):
    if settings.ENABLE_CAPTCHAS:
        captcha = CaptchaField(help_text=_(
            'This <a href="https://en.wikipedia.org/wiki/CAPTCHA">CAPTCHA</a> prevents '
            'automated SPAM. If you can\'t read it, just <a '
            'class="js-captcha-refresh">&#8634; reload</a> it.'
        ))
