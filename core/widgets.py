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

_fieldattrs = {'class': 'form-control', 'maxlength': 30}
_inputattrs = _fieldattrs.copy()
_inputattrs['autocomplete'] = 'off'
_selectattrs = _fieldattrs.copy()

TextWidget = forms.TextInput(attrs=_inputattrs)
PasswordWidget = forms.PasswordInput(attrs=_inputattrs)
SelectWidget = forms.Select(attrs={'class': 'form-control', })
