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


class ResetPasswordView(FormView):
    success_url = reverse_lazy('ResetPasswordThanks')
    template_name = 'reset/password.html'

    def get_context_data(self, **kwargs):
        context = super(ResetPasswordView, self).get_context_data(**kwargs)
        context['menuitem'] = 'email'
        return context


class ResetPasswordThanksView(TemplateView):
    template_name = 'reset/password-thanks.html'


class ResetPasswordConfirmationView(FormView):
    success_url = reverse_lazy('ResetPasswordConfirmationThanks')
    template_name = 'reset/password-confirmation.html'


class ResetPasswordConfirmationThanksView(TemplateView):
    template_name = 'reset/password-confirmationthanks.html'


class ResetEmailView(FormView):
    success_url = reverse_lazy('ResetEmailThanks')
    template_name = 'reset/email.html'

    def get_context_data(self, **kwargs):
        context = super(ResetEmailView, self).get_context_data(**kwargs)
        context['menuitem'] = 'email'
        return context


class ResetEmailThanksView(TemplateView):
    template_name = 'reset/email-thanks.html'


class ResetEmailConfirmationView(FormView):
    success_url = reverse_lazy('ResetEmailConfirmationThanks')
    template_name = 'reset/email-confirmation.html'


class ResetEmailConfirmationThanksView(TemplateView):
    template_name = 'reset/email-thanks.html'
