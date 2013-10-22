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

from datetime import datetime

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse_lazy
from django.forms.util import ErrorList
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import FormView
from django.views.generic import TemplateView

from brake.decorators import ratelimit

from core.constants import PURPOSE_REGISTER
from core.models import Confirmation
from core.exceptions import RateException
from core.exceptions import RegistrationRateException

from register.forms import RegistrationForm
from register.forms import RegistrationConfirmationForm

from backends import backend
from backends.base import UserExists
from backends.base import UserNotFound


class RegistrationView(CreateView):
    template_name = 'register/create.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('RegistrationThanks')

    CONFIRMATION_SUBJECT = _('Your new account on %(domain)s')

    @method_decorator(ratelimit(method='GET', rate='15/m'))
    @method_decorator(ratelimit(method='POST', rate='5/m'))
    def dispatch(self, request, *args, **kwargs):
        if getattr(request, 'limited', False):
            raise RateException()
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(RegistrationView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def registration_rate(self):
        # Check for a registration rate
        cache_key = 'registration-%s' % self.request.get_host()
        registrations = cache.get(cache_key, set())
        now = datetime.now()

        for key, value in settings.REGISTRATION_RATE.items():
            if len([s for s in registrations if s > now - key]) >= value:
                raise RegistrationRateException()
        registrations.add(now)
        cache.set(cache_key, registrations)

    def form_valid(self, form):
        self.registration_rate()

        try:
            username = form.cleaned_data['username']
            domain = form.cleaned_data['domain']
            email = form.cleaned_data['email']

            backend.create(username=username, domain=domain, email=email)
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
        key.send(
            request=self.request, template_base='register/mail',
            subject=self.CONFIRMATION_SUBJECT % {'domain': key.user.domain, })

        return response


class RegistrationThanksView(TemplateView):
    template_name = 'register/thanks.html'


class RegistrationConfirmationView(FormView):
    """Confirm a registration.

    .. NOTE:: This is deliberately not implemented as a generic view related
       to the Confirmation object. We want to present the form unconditionally
       and complain about a false key only when the user passed various
       Anti-SPAM measures.
    """
    form_class = RegistrationConfirmationForm
    template_name = 'register/confirm.html'
    success_url = reverse_lazy('RegistrationConfirmationThanks')

    def get_form_kwargs(self):
        kwargs = super(RegistrationConfirmationView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

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


class RegistrationConfirmationThanksView(TemplateView):
    template_name = 'register/confirmation-thanks.html'
