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

from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from core.constants import PURPOSE_REGISTER
from core.exceptions import RegistrationRateException
from core.views import ConfirmationView
from core.views import ConfirmedView

from register.forms import RegistrationForm
from register.forms import RegistrationConfirmationForm

from backends import backend

User = get_user_model()


class RegistrationView(ConfirmationView):
    template_name = 'register/create.html'
    form_class = RegistrationForm

    confirm_url_name = 'RegistrationConfirmation'
    email_subject = _('Your new account on %(domain)s')
    email_template = 'register/mail'
    purpose = PURPOSE_REGISTER

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        context['menuitem'] = 'register'
        context['username_help_text'] = context['form'].fields['username'].help_text % {
            'MIN_LENGTH': settings.MIN_USERNAME_LENGTH,
            'MAX_LENGTH': settings.MAX_USERNAME_LENGTH,
        }
        return context

    def registration_rate(self):
        # Check for a registration rate
        cache_key = 'registration-%s' % self.request.get_host()
        registrations = cache.get(cache_key, set())
        _now = datetime.utcnow()

        for key, value in settings.REGISTRATION_RATE.items():
            if len([s for s in registrations if s > _now - key]) >= value:
                raise RegistrationRateException()
        registrations.add(_now)
        cache.set(cache_key, registrations)

    def get_user(self, data):
        return User.objects.create(username=data['username'],
                                   domain=data['domain'], email=data['email'])

    def handle_valid(self, form, user):
        if settings.XMPP_HOSTS[user.domain].get('RESERVE', False):
            backend.reserve(username=user.username, domain=user.domain,
                            email=user.email)

    def form_valid(self, form):
        self.registration_rate()
        return super(RegistrationView, self).form_valid(form)


class RegistrationConfirmationView(ConfirmedView):
    """Confirm a registration.

    .. NOTE:: This is deliberately not implemented as a generic view related
       to the Confirmation object. We want to present the form unconditionally
       and complain about a false key only when the user passed various
       Anti-SPAM measures.
    """
    form_class = RegistrationConfirmationForm
    template_name = 'register/confirm.html'
    purpose = PURPOSE_REGISTER

    def handle_key(self, key, form):
        key.user.confirmed = now()
        key.user.save()

        backend.create(username=key.user.username, domain=key.user.domain,
                       email=key.user.email, password=form.cleaned_data['password'])
        if settings.WELCOME_MESSAGE is not None:
            reset_pass_path = reverse('ResetPassword')
            reset_mail_path = reverse('ResetEmail')
            delete_path = reverse('Delete')

            context = {
                'username': key.user.username,
                'domain': key.user.domain,
                'email': key.user.email,
                'password_reset_url': self.request.build_absolute_uri(location=reset_pass_path),
                'email_reset_url': self.request.build_absolute_uri(location=reset_pass_path),
                'delete_url': self.request.build_absolute_uri(location=reset_pass_path),
                'contact_url': settings.CONTACT_URL,
            }
            subject = settings.WELCOME_MESSAGE['subject'].format(**context)
            message = settings.WELCOME_MESSAGE['message'].format(**context)
            backend.send_message(username=key.user.username, domain=key.user.domain,
                                 subject=subject, message=message)
