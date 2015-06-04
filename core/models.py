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

import json
import logging
import random
import re
import smtplib
import string

from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import models
from django.template.loader import render_to_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l

from django.contrib.auth.models import AbstractBaseUser

from core.constants import PURPOSE_DELETE
from core.constants import PURPOSE_REGISTER
from core.constants import PURPOSE_SET_EMAIL
from core.constants import PURPOSE_SET_PASSWORD
from core.constants import REGISTRATION_INBAND
from core.constants import REGISTRATION_WEBSITE
from core.constants import REGISTRATION_UNKNOWN
from core.managers import ConfirmationManager
from core.managers import RegistrationUserManager
from core.querysets import ConfirmationQuerySet

from backends import backend
from backends.base import UserNotFound

PASSWORD_CHARS = string.ascii_letters + string.digits
PURPOSE_CHOICES = (
    (PURPOSE_REGISTER, 'registration'),
    (PURPOSE_SET_PASSWORD, 'set password'),
    (PURPOSE_SET_EMAIL, 'set email'),
    (PURPOSE_DELETE, 'delete'),
)
PURPOSE_DICT = dict(PURPOSE_CHOICES)

REGISTRATION_CHOICES = (
    (REGISTRATION_WEBSITE, 'Via Website'),
    (REGISTRATION_INBAND, 'In-Band Registration'),
    (REGISTRATION_UNKNOWN, 'Unknown'),
)
REGISTRATION_DICT = dict(REGISTRATION_CHOICES)
PURPOSES = {
    PURPOSE_REGISTER: {
        'urlname': 'RegistrationConfirmation',
        'subject': _l('Your new account on %(domain)s'),
        'template': 'register/mail',
    },
    PURPOSE_SET_EMAIL: {
        'urlname': 'ResetEmailConfirmation',
        'subject': _l('Confirm the email address for your %(domain)s account'),
        'template': 'reset/email-mail',
    },
    PURPOSE_SET_PASSWORD: {
        'urlname': 'ResetPasswordConfirmation',
        'subject': _l('Reset the password for your %(domain)s account'),
        'template': 'reset/password-mail',
    },
    PURPOSE_DELETE: {
        'urlname': 'DeleteConfirmation',
        'subject': _l('Delete your account on %(domain)s'),
        'template': 'delete/mail',
    },
}

log = logging.getLogger(__name__)
pgp_version = MIMENonMultipart('application', 'pgp-encrypted')
pgp_version.add_header('Content-Description', 'PGP/MIME version identification')
pgp_version.set_payload('Version: 1\n')


@python_2_unicode_compatible
class RegistrationUser(AbstractBaseUser):
    # NOTE: MySQL only allows a 255 character limit
    jid = models.CharField(max_length=255, unique=True, verbose_name='JID')
    email = models.EmailField(null=True, blank=True)
    gpg_fingerprint = models.CharField(max_length=40, null=True, blank=True)

    # when the account was first registered
    registered = models.DateTimeField(auto_now_add=True)
    registration_method = models.SmallIntegerField(choices=REGISTRATION_CHOICES)

    # when the email was confirmed
    confirmed = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = RegistrationUserManager()

    USERNAME_FIELD = 'jid'
    REQUIRED_FIELDS = ('email', )

    class Meta:
        verbose_name = _('User')

    def has_email(self):
        if not self.email or not self.confirmed:
            raise UserNotFound(
                _("You have either not yet set your email address or have not confirmed it yet."))
        return True

    def set_password(self, raw_password):
        if raw_password is None:
            self.set_unusable_password()
        else:
            backend.set_password(self.username, self.domain, raw_password)

    def check_password(self, raw_password):
        return backend.check_password(self.username, self.domain, raw_password)

    def set_unusable_password(self):
        pwd = ''.join(random.choice(PASSWORD_CHARS) for x in range(16))
        backend.set_unusable_password(self.username, self.domain, pwd)

    def send_confirmation(self, request, purpose, payload=None, **kwargs):
        if payload is None:
            payload = {}

        key = Confirmation.objects.create(user=self, purpose=purpose, payload=json.dumps(payload))
        key.send(request, **kwargs)
        return key

    def get_short_name(self):
        return self.email

    def has_usable_password(self):
        return backend.has_usable_password(self.username, self.domain)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def __str__(self):
        return self.jid

    @property
    def username(self):
        return self.jid.split('@', 1)[0]

    @property
    def domain(self):
        return self.jid.split('@', 1)[1]

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    @is_staff.setter
    def is_staff(self, value):
        self.is_admin = value


@python_2_unicode_compatible
class Confirmation(models.Model):
    key = models.CharField(max_length=40)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    created = models.DateTimeField(auto_now_add=True)
    purpose = models.SmallIntegerField(choices=PURPOSE_CHOICES)
    payload = models.TextField(null=True, blank=True)

    objects = ConfirmationManager.from_queryset(ConfirmationQuerySet)()

    def handle_gpg(self, site, subject, text, html):
        """
        :param site: Matching dict from XMPP_HOSTS.
        :param text: The text part of the message.
        :param html: The HTML part of the message.
        """
        gpg = settings.GPG
        encrypt = False
        signer = site.get('GPG_FINGERPRINT')
        sign = False

        payload = json.loads(self.payload)
        gpg_fingerprint = payload.get('gpg_fingerprint')
        recipient = payload.get('email', self.user.email)

        # encrypt only if the user has a fingerprint
        if gpg and gpg_fingerprint:
            # Receive key of recipient. We don't care about the result, because user might not have
            # uploaded it.
            gpg.recv_keys(settings.GPG_KEYSERVER, gpg_fingerprint)

            if gpg_fingerprint not in [k['fingerprint'] for k in gpg.list_keys()]:
                log.warn('%s: Unknown GPG fingerprint for %s', site['DOMAIN'], self.user.jid)
            else:
                encrypt = True

        frm = site.get('FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        msg = EmailMultiAlternatives(subject, from_email=frm, to=[recipient])

        # sign only if the user has fingerprint or signing is forced
        if gpg:
            if not signer:
                log.warn('%s: No GPG key configured, not signing', site['DOMAIN'])
            elif signer not in [k['fingerprint'] for k in gpg.list_keys(True)]:
                log.warn('%s: %s: secret key not found, not signing', site['DOMAIN'], signer)
                signer = None
            elif gpg and (gpg_fingerprint or settings.FORCE_GPG_SIGNING):
                sign = True

        # we create an unencrypted and unsigned message that we can send in case GPG fails
        default_msg = EmailMultiAlternatives(subject, from_email=frm, to=[recipient])
        default_msg.body = text
        default_msg.attach_alternative(html, 'text/html')

        if not (sign or encrypt):  # shortcut if no GPG is used
            return default_msg

        text = MIMEText(text, _charset='utf-8')
        html = MIMEText(html, _subtype='html', _charset='utf-8')
        body = MIMEMultipart(_subtype='alternative', _subparts=[text, html])

        if sign and not encrypt:  # only sign the message
            signed_body = gpg.sign(body.as_string(), keyid=site['GPG_FINGERPRINT'], detach=True)
            if not signed_body.data:
                log.warn('GPG returned no data when signing')
                log.warn(signed_body.stderr)
                return default_msg
            sig = MIMEBase(_maintype='application', _subtype='pgp-signature', name='signature.asc')
            sig.set_payload(signed_body.data)
            sig.add_header('Content-Description', 'OpenPGP digital signature')
            sig.add_header('Content-Disposition', 'attachment; filename="signature.asc"')
            del sig['Content-Transfer-Encoding']

            msg.mixed_subtype = 'signed'
            msg.attach(body)
            msg.attach(sig)
            protocol = 'application/pgp-signature'
        elif encrypt:  # encrypt and (possibly) sign
            encrypted_body = gpg.encrypt(body.as_string(), [gpg_fingerprint], sign=signer,
                                         always_trust=True)
            if not encrypted_body.data:
                log.warn('GPG returned no data when signing/encrypting')
                log.warn(encrypted_body.stderr)
                return default_msg
            encrypted = MIMEBase(_maintype='application', _subtype='octed-stream', name='encrypted.asc')
            encrypted.set_payload(encrypted_body.data)
            encrypted.add_header('Content-Description', 'OpenPGP encrypted message')
            encrypted.add_header('Content-Disposition', 'inline; filename="encrypted.asc"')
            msg.mixed_subtype = 'encrypted'
            msg.attach(pgp_version)
            msg.attach(encrypted)
            protocol = 'application/pgp-encrypted'

        # We wrap the message() method to set Content-Type parameters (set_params())
        _msg = msg.message
        def message():
            msg = _msg()
            msg.set_param('protocol', protocol)
            return msg
        msg.message = message

        return msg

    def send(self, request, lang='en'):
        path = reverse(PURPOSES[self.purpose]['urlname'], kwargs={'key': self.key, })
        uri = request.build_absolute_uri(location=path)

        subject = PURPOSES[self.purpose]['subject'] % {
            'domain': self.user.domain,
        }
        context = {
            'username': self.user.username,
            'domain': self.user.domain,
            'jid': self.user.jid,
            'user': self.user,
            'cleartext': settings.CLEARTEXT_PASSWORDS,
            'key': self,
            'uri': uri,
            'lang': lang,
            'subject': subject,
        }
        text = render_to_string('%s.txt' % PURPOSES[self.purpose]['template'], context)
        text = re.sub('\n\n+', '\n\n', text)
        html = render_to_string('%s.html' % PURPOSES[self.purpose]['template'], context)

        msg = self.handle_gpg(request.site, subject, text, html)

        try:
            msg.send()
        except smtplib.SMTPRecipientsRefused:
            pass

    def __str__(self):
        return '%s: %s' % (PURPOSE_DICT[self.purpose], self.user.jid)


@python_2_unicode_compatible
class Address(models.Model):
    address = models.GenericIPAddressField()
    activities = models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserAddresses')

    class Meta:
        verbose_name = _('IP-Address')
        verbose_name_plural = _('IP-Addresses')

    def __str__(self):
        return self.address


@python_2_unicode_compatible
class UserAddresses(models.Model):
    address = models.ForeignKey(Address)
    user = models.ForeignKey(RegistrationUser)

    timestamp = models.DateTimeField(auto_now_add=True)
    purpose = models.SmallIntegerField(choices=PURPOSE_CHOICES)

    class Meta:
        verbose_name = _('IP-Address Activity')
        verbose_name_plural = _('IP-Address Activities')


    def __str__(self):
        return '%s: %s/%s' % (PURPOSE_DICT[self.purpose], self.address.address,
                              self.user.jid)
