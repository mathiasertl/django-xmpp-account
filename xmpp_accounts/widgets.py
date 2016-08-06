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

from django import forms
from django.conf import settings


class XMPPAccountEmailWidget(forms.EmailInput):
    class Media:
        js = (
            'xmpp_accounts/js/email_widget.js',
        )


class XMPPAccountNodeWidget(forms.CharField):
    def clean(self, value):
        return super(XMPPAccountNodeWidget, self).clean(value).lower().strip()


class XMPPAccountJIDWidget(forms.MultiWidget):
    def decompress(self, value):
        if value:
            return value.split('@', 1)
        return '', settings.DEFAULT_XMPP_HOST

    class Media:
        js = (
            'xmpp_accounts/js/jid_widget.js',
        )
