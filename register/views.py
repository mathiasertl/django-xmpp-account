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

import json

from datetime import datetime

import pytz

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from core.constants import PURPOSE_REGISTER
from core.constants import REGISTRATION_WEBSITE
from core.exceptions import RegistrationRateException
from core.views import ConfirmationView
from core.views import ConfirmedView

from register.forms import RegistrationForm
from register.forms import RegistrationConfirmationForm

from backends import backend

User = get_user_model()
tzinfo = pytz.timezone(settings.TIME_ZONE)

_messages = {
    'opengraph_title': _('%(DOMAIN)s: Register a new account'),
    'opengraph_description': _('Register on %(DOMAIN)s, a reliable and secure Jabber server. Jabber is a free and open instant messaging protocol used by millions of people worldwide.'),
}


class RegistrationView(ConfirmationView):
    template_name = 'register/create.html'
    form_class = RegistrationForm

    purpose = PURPOSE_REGISTER
    menuitem = 'register'
    opengraph_title = _messages['opengraph_title']
    opengraph_description = _messages['opengraph_description']

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        form = context['form']
        context['username_help_text'] = form.fields['username'].help_text % {
            'MIN_LENGTH': settings.MIN_USERNAME_LENGTH,
            'MAX_LENGTH': settings.MAX_USERNAME_LENGTH,
        }

        if hasattr(form, 'cleaned_data') and hasattr(form, '_username_status'):  # form was submitted
            context['username_status'] = form._username_status
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

    def get_form_kwargs(self):
        """Override to remove the intial domain if registration is turned off."""
        kwargs = super(RegistrationView, self).get_form_kwargs()
        if self.request.site.get('REGISTRATION', True) is False:
            del kwargs['initial']['domain']
        return kwargs

    def get_user(self, data):
        last_login = tzinfo.localize(datetime.now())
        jid = '%s@%s' % (data['username'], data['domain'])
        return User.objects.create(jid=jid, last_login=last_login, email=data['email'],
                                   registration_method=REGISTRATION_WEBSITE,
        )

    def handle_valid(self, form, user):
        domain = form.cleaned_data['domain']
        payload = self.handle_gpg(form, user)
        payload['email'] = form.cleaned_data['email']

        if settings.XMPP_HOSTS[domain].get('RESERVE', False):
            backend.reserve(
                username=form.cleaned_data['username'], domain=domain, email=user.email)
        return payload

    def form_valid(self, form):
        self.registration_rate()
        return super(RegistrationView, self).form_valid(form)


class RegistrationConfirmationView(ConfirmedView):
    """Confirm a registration.

    .. NOTE:: This is deliberately not implemented as a generic view related to the Confirmation
       object. We want to present the form unconditionally and complain about a false key only when
       the user passed various Anti-SPAM measures.
    """
    form_class = RegistrationConfirmationForm
    template_name = 'register/confirm.html'
    purpose = PURPOSE_REGISTER
    menuitem = 'register'
    action_url = 'index'
    opengraph_title = _messages['opengraph_title']
    opengraph_description = _messages['opengraph_description']

    def handle_key(self, key, form):
        data = json.loads(key.payload)
        key.user.gpg_fingerprint = data.get('gpg_fingerprint')
        key.user.confirmed = now()
        key.user.save()

        backend.create(username=key.user.username, domain=key.user.domain, email=key.user.email,
                       password=form.cleaned_data['password'])
        if settings.WELCOME_MESSAGE is not None:
            reset_pass_path = reverse('ResetPassword')
            reset_mail_path = reverse('ResetEmail')
            delete_path = reverse('Delete')

            context = {
                'username': key.user.username,
                'domain': key.user.domain,
                'email': key.user.email,
                'password_reset_url': self.request.build_absolute_uri(location=reset_pass_path),
                'email_reset_url': self.request.build_absolute_uri(location=reset_mail_path),
                'delete_url': self.request.build_absolute_uri(location=delete_path),
                'contact_url': self.request.site['CONTACT_URL'],
            }
            subject = settings.WELCOME_MESSAGE['subject'].format(**context)
            message = settings.WELCOME_MESSAGE['message'].format(**context)
            backend.message(username=key.user.username, domain=key.user.domain, subject=subject,
                            message=message)
