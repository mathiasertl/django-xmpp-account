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

from django.core.urlresolvers import reverse_lazy
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _
from django.views.generic import CreateView
from django.views.generic import FormView

from register.forms import RegistrationForm
from register.forms import RegistrationConfirmationForm
from backends import backend
from backends.base import UserExists


class RegistrationView(CreateView):
    template_name = 'register/create.html'
    form_class = RegistrationForm
    success_url = '/'

    def form_valid(self, form):
        try:
            backend.create(**form.cleaned_data)
        except UserExists:
            # if the user already exists, this form is invalid!
            errors = form._errors.setdefault("username", ErrorList())
            errors.append(_("User already exists!"))
            return self.form_invalid(form)

        return super(RegistrationView, self).form_valid(form)


class RegistrationConfirmationView(FormView):
    form_class = RegistrationConfirmationForm
    template_name = 'register/confirm.html'
    success_url = reverse_lazy('RegistrationThanks')

    def form_valid(self, form):
        return super(FormView, self).form_valid(form)
