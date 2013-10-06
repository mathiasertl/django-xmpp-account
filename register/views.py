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

import random
import string

from django.forms.util import ErrorList
from django.utils.translation import ugettext as _
from django.views.generic import FormView

from register.forms import RegistrationForm
from backends import backend
from backends.base import UserExists


def random_password():
    return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(16))


class IndexView(FormView):
    template_name = 'index.html'
    form_class = RegistrationForm
    success_url = '/'

    def form_valid(self, form):
        data = form.cleaned_data
        try:
            tmp_password = random_password()
            backend.create(username=data['username'], password=tmp_password,
                           host=data['host'], email=data['email'])
        except UserExists:
            # if the user already exists, this form is invalid!
            errors = form._errors.setdefault("username", ErrorList())
            errors.append(_("User already exists!"))
            return self.form_invalid(form)

        return super(IndexView, self).form_valid(form)
