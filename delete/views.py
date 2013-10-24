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

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView
from django.views.generic import TemplateView

from delete.forms import DeleteForm
from delete.forms import DeleteConfirmationForm


class DeleteView(FormView):
    form_class = DeleteForm
    success_url = reverse_lazy('DeleteThanks')
    template_name = 'delete/delete.html'

    def get_form_kwargs(self):
        kwargs = super(DeleteView, self).get_form_kwargs()
        if settings.RECAPTCHA_CLIENT is not None:
            kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['menuitem'] = 'delete'
        return context


class DeleteThanksView(TemplateView):
    template_name = 'delete/delete-thanks.html'


class DeleteConfirmationView(FormView):
    form_class = DeleteConfirmationForm
    success_url = reverse_lazy('DeleteConfirmationThanks')
    template_name = 'delete/delete-confirm.html'

    def get_form_kwargs(self):
        kwargs = super(DeleteConfirmationView, self).get_form_kwargs()
        if settings.RECAPTCHA_CLIENT is not None:
            kwargs['request'] = self.request
        return kwargs


class DeleteConfirmationThanksView(TemplateView):
    template_name = 'delete/delete-confirm-thanks.html'
