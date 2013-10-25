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
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.forms.util import ErrorList
from django.utils.translation import ugettext as _
from django.views.generic import FormView
from django.views.generic import TemplateView

from core.constants import PURPOSE_SET_PASSWORD
from core.constants import PURPOSE_SET_EMAIL
from core.models import Confirmation
from core.views import AntiSpamFormView

from reset.forms import ResetPasswordForm
from reset.forms import ResetPasswordConfirmationForm
from reset.forms import ResetEmailForm
from reset.forms import ResetEmailConfirmationForm

User = get_user_model()


class ResetPasswordView(AntiSpamFormView):
    form_class = ResetPasswordForm
    success_url = reverse_lazy('ResetPasswordThanks')
    template_name = 'reset/password.html'

    purpose = PURPOSE_SET_PASSWORD
    email_subject = _('Reset the password for your %(domain)s account')
    email_template = 'reset/password-mail'

    def get_context_data(self, **kwargs):
        context = super(ResetPasswordView, self).get_context_data(**kwargs)
        context['menuitem'] = 'password'
        return context

    def form_valid(self, form):
        data = form.cleaned_data

        try:
            user = User.objects.get(email=data['email'],
                                    username=data['username'],
                                    domain=data['domain'])
# TODO: use a class-based queryset?
        except User.DoesNotExist:
            errors = form._errors.setdefault(forms.forms.NON_FIELD_ERRORS,
                                             ErrorList())
            errors.append(_("User not found!"))
            return self.form_invalid(form)

        # get the response
        response = super(ResetPasswordView, self).form_valid(form)

        # create a confirmation key before returning the response
        key = Confirmation.objects.create(user=user, purpose=self.purpose)
        key.send(
            request=self.request, template_base=self.email_template,
            subject=self.email_subject % {'domain': user.domain, })

        return response

class ResetPasswordThanksView(TemplateView):
    template_name = 'reset/password-thanks.html'


class ResetPasswordConfirmationView(FormView):
    form_class = ResetPasswordConfirmationForm
    success_url = reverse_lazy('ResetPasswordConfirmationThanks')
    template_name = 'reset/password-confirm.html'

    def get_form_kwargs(self):
        kwargs = super(ResetPasswordConfirmationView, self).get_form_kwargs()
        if settings.RECAPTCHA_CLIENT is not None:
            kwargs['request'] = self.request
        return kwargs


class ResetPasswordConfirmationThanksView(TemplateView):
    template_name = 'reset/password-confirm-thanks.html'


class ResetEmailView(FormView):
    form_class = ResetEmailForm
    success_url = reverse_lazy('ResetEmailThanks')
    template_name = 'reset/email.html'

    def get_form_kwargs(self):
        kwargs = super(ResetEmailView, self).get_form_kwargs()
        if settings.RECAPTCHA_CLIENT is not None:
            kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ResetEmailView, self).get_context_data(**kwargs)
        context['menuitem'] = 'email'
        return context


class ResetEmailThanksView(TemplateView):
    template_name = 'reset/email-thanks.html'


class ResetEmailConfirmationView(FormView):
    form_class = ResetEmailConfirmationForm
    success_url = reverse_lazy('ResetEmailConfirmationThanks')
    template_name = 'reset/email-confirm.html'

    def get_form_kwargs(self):
        kwargs = super(ResetEmailConfirmationView, self).get_form_kwargs()
        if settings.RECAPTCHA_CLIENT is not None:
            kwargs['request'] = self.request
        return kwargs


class ResetEmailConfirmationThanksView(TemplateView):
    template_name = 'reset/email-confirm-thanks.html'
