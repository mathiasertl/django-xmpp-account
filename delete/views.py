# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:hlsearch
#
# This file is part of django-xmpp-account (https://github.com/mathiasertl/django-xmpp-account/).
#
# django-xmpp-account is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# django-xmpp-account is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with django-xmpp-account.
# If not, see <http://www.gnu.org/licenses/>.

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
_messages = {
    'opengraph_title': _('%(DOMAIN)s: Delete your account'),
    'opengraph_description': _('Delete your account on %(DOMAIN)s. WARNING: Once your account is deleted, it can never be restored.'),
}


class DeleteView(ConfirmationView):
    form_class = DeleteForm
    template_name = 'delete/delete.html'

    confirm_url_name = 'DeleteConfirmation'
    purpose = PURPOSE_DELETE
    email_subject = _('Delete your account on %(domain)s')
    email_template = 'delete/mail'
    menuitem = 'delete'
    opengraph_title = _messages['opengraph_title']
    opengraph_description = _messages['opengraph_description']

    def get_user(self, data):
        username = data['username']
        domain = data['domain']

        try:
            user = User.objects.has_email().get_user(username, domain)
        except User.DoesNotExist:
            raise UserNotFound()

        if not backend.check_password(username=username, domain=domain, password=data['password']):
           raise UserNotFound()

        return user


class DeleteConfirmationView(ConfirmedView):
    form_class = DeleteConfirmationForm
    template_name = 'delete/delete-confirm.html'
    purpose = PURPOSE_DELETE
    action_url = 'Delete'
    opengraph_title = _messages['opengraph_title']
    opengraph_description = _messages['opengraph_description']

    def handle_key(self, key, form):
        username = key.user.username
        domain = key.user.domain
        password = form.cleaned_data['password']

        if not backend.check_password(username=username, domain=domain, password=password):
            raise UserNotFound()

    def after_delete(self, data):
        # actually delete user from the database
        print('TODO: use user-properties')
        username, domain = self.user.jid.split('@', 1)
        backend.remove(username=username, domain=domain)
        self.user.delete()
