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

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _

from backends import backend
from backends.base import UserNotFound

from core.constants import PURPOSE_SET_PASSWORD
from core.constants import PURPOSE_SET_EMAIL
from core.views import ConfirmationView
from core.views import ConfirmedView

from reset.forms import ResetPasswordForm
from reset.forms import ResetPasswordConfirmationForm
from reset.forms import ResetEmailForm
from reset.forms import ResetEmailConfirmationForm

User = get_user_model()


class ResetPasswordView(ConfirmationView):
    form_class = ResetPasswordForm
    success_url = reverse_lazy('ResetPasswordThanks')
    template_name = 'reset/password.html'

    confirm_url_name = 'ResetPasswordConfirmation'
    purpose = PURPOSE_SET_PASSWORD
    email_subject = _('Reset the password for your %(domain)s account')
    email_template = 'reset/password-mail'

    def get_context_data(self, **kwargs):
        context = super(ResetPasswordView, self).get_context_data(**kwargs)
        context['menuitem'] = 'password'
        return context

    def get_user(self, data):
        return User.objects.get(email=data['email'], username=data['username'],
                                domain=data['domain'])


class ResetPasswordConfirmationView(ConfirmedView):
    form_class = ResetPasswordConfirmationForm
    template_name = 'reset/password-confirm.html'
    purpose = PURPOSE_SET_PASSWORD

    def handle_key(self, key, form):
        backend.set_password(key.user.username, key.user.domain,
                             form.cleaned_data['password1'])


class ResetEmailView(ConfirmationView):
    form_class = ResetEmailForm
    success_url = reverse_lazy('ResetEmailThanks')
    template_name = 'reset/email.html'

    confirm_url_name = 'ResetEmailConfirmation'
    purpose = PURPOSE_SET_EMAIL
    email_subject = _('Confirm the email address for your %(domain)s account')
    email_template = 'reset/email-mail'

    def get_context_data(self, **kwargs):
        context = super(ResetEmailView, self).get_context_data(**kwargs)
        context['menuitem'] = 'email'
        return context

    def get_user(self, data):
        """User may or may not exist."""
        username = data['username']
        domain = data['domain']
        password = data['password']

        if not backend.check_password(username=username,
                                      domain=domain, password=password):
            raise UserNotFound()

        user, created = User.objects.get_or_create(
            username=data['username'], domain=data['domain'],
            defaults={'email': data['email']})

        if created:
            user.email = data['email']
            user.email_confirmed = False
            user.save()

        return user


class ResetEmailConfirmationView(ConfirmedView):
    form_class = ResetEmailConfirmationForm
    template_name = 'reset/email-confirm.html'
    purpose = PURPOSE_SET_EMAIL

    def handle_key(self, key, form):
        if not backend.check_password(username=key.user.username,
                                      domain=key.user.domain,
                                      password=form['password']):
            raise UserNotFound()
