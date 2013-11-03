# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-register (https://account.jabber.at/doc).
#
# django-xmpp-register is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# django-xmpp-register is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# django-xmpp-register.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from core.constants import PURPOSE_DELETE
from core.views import ConfirmationView
from core.views import ConfirmedView

from delete.forms import DeleteForm
from delete.forms import DeleteConfirmationForm

from backends import backend
from backends.base import UserNotFound

User = get_user_model()


class DeleteView(ConfirmationView):
    form_class = DeleteForm
    template_name = 'delete/delete.html'

    confirm_url_name = 'DeleteConfirmation'
    purpose = PURPOSE_DELETE
    email_subject = _('Delete your account on %(domain)s')
    email_template = 'delete/mail'

    def get_context_data(self, **kwargs):
        context = super(DeleteView, self).get_context_data(**kwargs)
        context['menuitem'] = 'delete'
        return context

    def get_user(self, data):
        username = data['username']
        domain = data['domain']
        if not backend.check_password(username=username, domain=domain,
                                      password=data['password']):
           raise UserNotFound()
        return User.objects.get(username=data['username'],
                                domain=data['domain'])


class DeleteConfirmationView(ConfirmedView):
    form_class = DeleteConfirmationForm
    template_name = 'delete/delete-confirm.html'
    purpose = PURPOSE_DELETE

    def handle_key(self, key, form):
        username = key.user.username
        domain = key.user.domain
        password = form.cleaned_data['password']

        if not backend.check_password(username=username, domain=domain,
                                      password=password):
            raise UserNotFound()

    def after_delete(self, data):
        # actually delete user from the database
        backend.remove(username=self.user.username, domain=self.user.domain)
        self.user.delete()
