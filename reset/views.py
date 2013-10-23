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

from django.views.generic import FormView
from django.views.generic import TemplateView


class ResetPasswordView(FormView):
    template_name = 'reset/password.html'

    def get_context_data(self, **kwargs):
        context = super(ResetPasswordView, self).get_context_data(**kwargs)
        context['menuitem'] = 'email'
        return context


class ResetPasswordConfirmationView(FormView):
    template_name = 'reset/password-confirmation.html'


class ResetPasswordThanksView(TemplateView):
    template_name = 'reset/password-thanks.html'


class ResetEmailView(FormView):
    template_name = 'reset/email.html'

    def get_context_data(self, **kwargs):
        context = super(ResetEmailView, self).get_context_data(**kwargs)
        context['menuitem'] = 'email'
        return context


class ResetEmailConfirmationView(FormView):
    template_name = 'reset/email-confirmation.html'


class ResetEmailThanksView(TemplateView):
    template_name = 'reset/email-thanks.html'
