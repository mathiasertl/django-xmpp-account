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
from django.core.mail import send_mail
from django.core.urlresolvers import reverse_lazy
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import TemplateView

from core.constants import PURPOSE_REGISTER
from core.models import Confirmation

from register.forms import RegistrationForm
from register.forms import RegistrationConfirmationForm

from backends import backend
from backends.base import UserExists
from backends.base import UserNotFound


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

        # get the response
        response = super(RegistrationView, self).form_valid(form)

        # create a confirmation key before returning the response
        key = Confirmation.objects.create(
            user=self.object, purpose=PURPOSE_REGISTER,
            key=Confirmation.objects.get_key(form.cleaned_data['email']))

        send_mail(subject=_('Your account on %(domain)s') % {'domain': self.object.domain},
                  message=key.key,
                  from_email=settings.DEFAULT_FROM_EMAIL,
                  recipient_list=[self.object.email])

        return response


class RegistrationConfirmationView(FormView):
    """Confirm a registration.

    .. NOTE:: This is deliberately not implemented as a generic view related
       to the Confirmation object. We want to present the form unconditionally
       and complain about a false key only when the user passed various
       Anti-SPAM measures.
    """
    form_class = RegistrationConfirmationForm
    template_name = 'register/confirm.html'
    success_url = reverse_lazy('RegistrationThanks')

    def form_valid(self, form):
        key = Confirmation.objects.registrations().get(key=self.kwargs['key'])
        try:
            backend.set_password(
                username=key.user.username, domain=key.user.domain,
                password=form.cleaned_data['password1'])
        except UserNotFound:  # shouldn't really happen, user was just created
            errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS,
                                             ErrorList())
            errors.append(_("User not found!"))
            return self.form_invalid(form)

        return super(FormView, self).form_valid(form)


class RegistrationThanksView(TemplateView):
    template_name = 'register/thanks.html'
