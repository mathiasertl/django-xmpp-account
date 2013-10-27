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
from django.utils.translation import ugettext as _

_fieldattrs = {'class': 'form-control', 'maxlength': 30, }
_emailattrs = _fieldattrs.copy()
_emailattrs['type'] = 'email'
_emailattrs['placeholder'] = _("Enter Email")

TextWidget = forms.TextInput(attrs=_fieldattrs)
PasswordWidget = forms.PasswordInput(attrs=_fieldattrs)
EmailWidget = forms.TextInput(attrs=_emailattrs)
SelectWidget = forms.Select(attrs=_fieldattrs)
