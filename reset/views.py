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
from django.views.generic import FormView
from django.views.generic import TemplateView

from reset.forms import ResetPasswordForm
from reset.forms import ResetPasswordConfirmationForm
from reset.forms import ResetEmailForm
from reset.forms import ResetEmailConfirmationForm


class ResetPasswordView(FormView):
    form_class = ResetPasswordForm
    success_url = reverse_lazy('ResetPasswordThanks')
    template_name = 'reset/password.html'

    def get_context_data(self, **kwargs):
        context = super(ResetPasswordView, self).get_context_data(**kwargs)
        context['menuitem'] = 'email'
        return context


class ResetPasswordThanksView(TemplateView):
    template_name = 'reset/password-thanks.html'


class ResetPasswordConfirmationView(FormView):
    form_class = ResetPasswordConfirmationForm
    success_url = reverse_lazy('ResetPasswordConfirmationThanks')
    template_name = 'reset/password-confirmation.html'


class ResetPasswordConfirmationThanksView(TemplateView):
    template_name = 'reset/password-confirmationthanks.html'


class ResetEmailView(FormView):
    form_class = ResetEmailForm
    success_url = reverse_lazy('ResetEmailThanks')
    template_name = 'reset/email.html'

    def get_context_data(self, **kwargs):
        context = super(ResetEmailView, self).get_context_data(**kwargs)
        context['menuitem'] = 'email'
        return context


class ResetEmailThanksView(TemplateView):
    template_name = 'reset/email-thanks.html'


class ResetEmailConfirmationView(FormView):
    form_class = ResetEmailConfirmationForm
    success_url = reverse_lazy('ResetEmailConfirmationThanks')
    template_name = 'reset/email-confirmation.html'


class ResetEmailConfirmationThanksView(TemplateView):
    template_name = 'reset/email-thanks.html'
