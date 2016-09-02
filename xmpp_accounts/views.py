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

from __future__ import unicode_literals, absolute_import

import json

from datetime import datetime

import pytz

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.utils.six.moves.urllib.parse import urlsplit
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from django.views.generic import FormView
from django.views.generic import View

from core.exceptions import RegistrationRateException
from core.views import ConfirmationView
from core.views import ConfirmedView

from .constants import PURPOSE_DELETE
from .constants import PURPOSE_REGISTER
from .constants import PURPOSE_SET_EMAIL
from .constants import PURPOSE_SET_PASSWORD
from .constants import REGISTRATION_WEBSITE
from .forms import DeleteConfirmationForm
from .forms import DeleteForm
from .forms import RegistrationConfirmationForm
from .forms import RegistrationForm
from .forms import ResetEmailConfirmationForm
from .forms import ResetEmailForm
from .forms import ResetPasswordConfirmationForm
from .forms import ResetPasswordForm
from .mixins import AntiSpamMixin
from .mixins import ConfirmationMixin
from .mixins import ConfirmedMixin

from django_xmpp_backends import backend
from xmpp_backends.base import UserNotFound

User = get_user_model()
tzinfo = pytz.timezone(settings.TIME_ZONE)
_messages = {
    PURPOSE_REGISTER: {
        'opengraph_title': _('%(DOMAIN)s: Register a new account'),
        'opengraph_description': _('Register on %(DOMAIN)s, a reliable and secure Jabber server. Jabber is a free and open instant messaging protocol used by millions of people worldwide.'),
    },
    PURPOSE_SET_EMAIL: {
        'opengraph_title': _('%(DOMAIN)s: Set a new email address'),
        'opengraph_description': _('Set a new email address for your Jabber account on %(DOMAIN)s. You must have a valid email address set to be able to reset your password.'),
    },
    PURPOSE_SET_PASSWORD: {
        'opengraph_title': _('%(DOMAIN)s: Reset your password'),
        'opengraph_description': _('Reset the password for your %(DOMAIN)s account.'),
    },
    PURPOSE_DELETE: {
        'opengraph_title': _('%(DOMAIN)s: Delete your account'),
        'opengraph_description': _('Delete your account on %(DOMAIN)s. WARNING: Once your account is deleted, it can never be restored.'),
    },
}


class XMPPAccountView(AntiSpamMixin, FormView):
    """Base class for all other views in this module."""

    purpose = None

    def get_context_data(self, **kwargs):
        context = super(XMPPAccountView, self).get_context_data(**kwargs)
        context['menuitem'] = self.purpose

        # Social media
        action_path = reverse('xmpp_accounts:%s' % self.purpose)
        context['ACTION_URL'] = self.request.build_absolute_uri(action_path)
        context['REGISTER_URL'] = self.request.build_absolute_uri(
            reverse('xmpp_accounts:register'))
        context['OPENGRAPH_TITLE'] = _messages[self.purpose]['opengraph_title'] % self.request.site
        context['OPENGRAPH_DESCRIPTION'] = _messages[self.purpose]['opengraph_description'] \
                                            % self.request.site
        context['TWITTER_TEXT'] = _messages[self.purpose].get('twitter_text',
                                                              context['OPENGRAPH_TITLE'])

        if 'CANONICAL_HOST' in self.request.site:
            context['ACTION_URL'] = urlsplit(context['ACTION_URL'])._replace(
                netloc=self.request.site['CANONICAL_HOST']).geturl()
            context['REGISTER_URL'] = urlsplit(context['REGISTER_URL'])._replace(
                netloc=self.request.site['CANONICAL_HOST']).geturl()

        # TODO: Yes, that's ugly!
        form = context['form']
        if settings.GPG and hasattr(form, 'cleaned_data') and 'gpg_key' in form.fields:
            if form['gpg_key'].errors or form['fingerprint'].errors or \
                    form.cleaned_data.get('fingerprint') or form.cleaned_data.get('gpg_key'):
                context['show_gpg'] = True
        return context

    def form_valid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class RegistrationView(ConfirmationMixin, XMPPAccountView):
    form_class = RegistrationForm
    purpose = PURPOSE_REGISTER

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
        last_login = tzinfo.localize(datetime.now())
        return User.objects.create(jid=data['username'], last_login=last_login,
                                   email=data['email'], registration_method=REGISTRATION_WEBSITE)

    def handle_valid(self, form, user):
        node, domain = user.get_username().split('@', 1)
        if settings.XMPP_HOSTS[domain].get('RESERVE', False):
            backend.create_reservation(username=node, domain=domain, email=user.email)

        kwargs = {
            'recipient': user.email,
        }
        kwargs.update(self.gpg_from_form(form))
        return kwargs

    def form_valid(self, form):
        self.registration_rate()
        with transaction.atomic():
            return super(RegistrationView, self).form_valid(form)


class RegistrationConfirmationView(ConfirmedMixin, XMPPAccountView):
    """Confirm a registration.

    .. NOTE:: This is deliberately not implemented as a generic view related to the Confirmation
       object. We want to present the form unconditionally and complain about a false key only when
       the user passed various Anti-SPAM measures.
    """
    form_class = RegistrationConfirmationForm
    purpose = PURPOSE_REGISTER

    def handle_key(self, key, user, form):
        user.gpg_fingerprint = json.loads(key.payload).get('gpg_encrypt')
        user.confirmed = now()
        user.save()

        backend.create_user(username=user.node, domain=user.domain, email=user.email,
                            password=form.cleaned_data['password'])
        if settings.WELCOME_MESSAGE is not None:
            reset_pass_path = reverse('xmpp_accounts:password')
            reset_mail_path = reverse('xmpp_accounts:reset_email')
            delete_path = reverse('xmpp_accounts:delete')

            context = {
                'username': user.node,
                'domain': user.domain,
                'email': user.email,
                'password_reset_url': self.request.build_absolute_uri(location=reset_pass_path),
                'email_reset_url': self.request.build_absolute_uri(location=reset_mail_path),
                'delete_url': self.request.build_absolute_uri(location=delete_path),
                'contact_url': self.request.site['CONTACT_URL'],
            }
            subject = settings.WELCOME_MESSAGE['subject'].format(**context)
            message = settings.WELCOME_MESSAGE['message'].format(**context)
            backend.message_user(username=user.node, domain=user.domain, subject=subject,
                                 message=message)


class ResetPasswordView(ConfirmationMixin, XMPPAccountView):
    form_class = ResetPasswordForm
    purpose = PURPOSE_SET_PASSWORD

    def handle_valid(self, form, user):
        payload = self.gpg_from_user(user)
        payload['recipient'] = user.email
        return payload

    def get_user(self, data):
        return User.objects.has_email().get(jid=data['username'])


class ResetPasswordConfirmationView(ConfirmedMixin, XMPPAccountView):
    form_class = ResetPasswordConfirmationForm
    purpose = PURPOSE_SET_PASSWORD

    def handle_key(self, key, user, form):
        node, domain = user.get_username().split('@', 1)
        backend.set_password(username=node, domain=domain, password=form.cleaned_data['password'])
        user.confirmed = now()
        user.save()


class ResetEmailView(ConfirmationMixin, XMPPAccountView):
    form_class = ResetEmailForm
    purpose = PURPOSE_SET_EMAIL

    def get_user(self, data):
        return User.objects.get(jid=data['username'])

    def handle_valid(self, form, user):
        payload = self.gpg_from_form(form)
        payload['recipient'] = form.cleaned_data['email']
        return payload


class ResetEmailConfirmationView(ConfirmedMixin, XMPPAccountView):
    form_class = ResetEmailConfirmationForm
    purpose = PURPOSE_SET_EMAIL

    def handle_key(self, key, user, form):
        if not backend.check_password(username=key.user.node, domain=key.user.domain,
                                      password=form.cleaned_data['password']):
            raise UserNotFound()

        data = json.loads(key.payload)
        user.gpg_fingerprint = data.get('gpg_fingerprint')
        user.confirmed = now()

        if 'recipient' in data:
            user.email = data['recipient']
        elif 'email' in data:
            user.email = data['email']

        user.save()
        backend.set_email(username=user.node, domain=user.domain, email=user.email)


class DeleteView(ConfirmationMixin, XMPPAccountView):
    form_class = DeleteForm
    purpose = PURPOSE_DELETE

    def handle_valid(self, form, user):
        payload = self.gpg_from_user(user)
        payload['recipient'] = user.email
        return payload

    def get_user(self, data):
        try:
            user = User.objects.has_email().get(jid=data['username'])
        except User.DoesNotExist:
            raise UserNotFound()

        node, domain = user.jid.split('@', 1)
        if not backend.check_password(username=node, domain=domain, password=data['password']):
           raise UserNotFound()

        return user


class DeleteConfirmationView(ConfirmedMixin, XMPPAccountView):
    form_class = DeleteConfirmationForm
    purpose = PURPOSE_DELETE

    def handle_key(self, key, user, form):
        username = user.node
        domain = user.domain
        password = form.cleaned_data['password']

        if not backend.check_password(username=username, domain=domain, password=password):
            raise UserNotFound()

    def after_delete(self, user, data):
        # actually delete user from the database
        backend.remove_user(username=user.node, domain=user.domain)
        self.user.delete()


class UserAvailableView(View):
    def post(self, request):
        # Note: XMPP usernames are case insensitive
        username = request.POST.get('username', '').strip().lower()
        domain = request.POST.get('domain', '').strip().lower()
        jid = '%s@%s' % (username, domain)

        cache_key = 'exists_%s' % jid
        exists = cache.get(cache_key)
        if exists is True:
            return HttpResponse('', status=409)
        elif exists is False:
            return HttpResponse('')

        # Check if the user exists in the database
        if User.objects.filter(jid=jid).exists():
            cache.set(cache_key, True, 30)
            return HttpResponse('', status=409)

        # TODO: Add a setting to rely on the contents of the database and not ask the backend.

        # Check if the user exists in the backend
        if backend.user_exists(username, domain):
            cache.set(cache_key, True, 30)
            return HttpResponse('', status=409)
        else:
            cache.set(cache_key, False, 30)
            return HttpResponse('')
