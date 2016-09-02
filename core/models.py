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
import re
import smtplib
import string

from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l

from django_xmpp_backends.models import XmppBackendUser

from core.constants import PURPOSE_DELETE
from core.constants import PURPOSE_REGISTER
from core.constants import PURPOSE_SET_EMAIL
from core.constants import PURPOSE_SET_PASSWORD
from core.constants import NEW_PURPOSE_DELETE
from core.constants import NEW_PURPOSE_REGISTER
from core.constants import NEW_PURPOSE_SET_EMAIL
from core.constants import NEW_PURPOSE_SET_PASSWORD
from core.constants import REGISTRATION_INBAND
from core.constants import REGISTRATION_WEBSITE
from core.constants import REGISTRATION_UNKNOWN
from core.exceptions import GpgError
from core.exceptions import GpgFingerprintError
from core.exceptions import GpgKeyError
from core.exceptions import TemporaryError
from core.lock import GpgLock
from core.managers import ConfirmationManager
from core.managers import RegistrationUserManager
from core.querysets import ConfirmationQuerySet

from xmpp_backends.base import UserNotFound

PASSWORD_CHARS = string.ascii_letters + string.digits
PURPOSE_CHOICES = (
    (PURPOSE_REGISTER, 'registration'),
    (PURPOSE_SET_PASSWORD, 'set password'),
    (PURPOSE_SET_EMAIL, 'set email'),
    (PURPOSE_DELETE, 'delete'),
)
NEW_PURPOSE_CHOICES = (
    (NEW_PURPOSE_REGISTER, 'registration'),
    (NEW_PURPOSE_SET_PASSWORD, 'set password'),
    (NEW_PURPOSE_SET_EMAIL, 'set email'),
    (NEW_PURPOSE_DELETE, 'delete'),
)
PURPOSE_DICT = dict(PURPOSE_CHOICES)

REGISTRATION_CHOICES = (
    (REGISTRATION_WEBSITE, 'Via Website'),
    (REGISTRATION_INBAND, 'In-Band Registration'),
    (REGISTRATION_UNKNOWN, 'Unknown'),
)
REGISTRATION_DICT = dict(REGISTRATION_CHOICES)
PURPOSES = {
    NEW_PURPOSE_REGISTER: {
        'subject': _('Your new account on %(domain)s'),
    },
    NEW_PURPOSE_SET_PASSWORD: {
        'subject':  _('Reset the password for your %(domain)s account'),
    },
    NEW_PURPOSE_SET_EMAIL: {
        'subject': _l('Confirm the email address for your %(domain)s account'),
    },
    NEW_PURPOSE_DELETE: {
        'subject': _l('Delete your account on %(domain)s'),
    },
}

log = logging.getLogger(__name__)
pgp_version = MIMENonMultipart('application', 'pgp-encrypted')
pgp_version.add_header('Content-Description', 'PGP/MIME version identification')
pgp_version.set_payload('Version: 1\n')


@python_2_unicode_compatible
class RegistrationUser(XmppBackendUser):
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

    def has_email(self):
        if not self.email or not self.confirmed:
            raise UserNotFound(
                _("You have either not yet set your email address or have not confirmed it yet."))
        return True

    def get_confirmation_key(self, purpose, payload, request):
        try:
            payload = json.dumps(payload)
        except UnicodeDecodeError:
            raise TemporaryError(
                "It appears you have entered some weird characters. Please try again.")

        return self.confirmation_set.create(purpose=purpose, payload=payload)

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    def __str__(self):
        return self.jid

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
    purpose = models.CharField(max_length=12, choices=NEW_PURPOSE_CHOICES)
    payload = models.TextField(null=True, blank=True)

    objects = ConfirmationManager.from_queryset(ConfirmationQuerySet)()

    def should_use_gpg(self, payload, site):
        if not settings.GPG:  # GPG not configured
            return False

        if payload.get('gpg_fingerprint') or payload.get('gpg_key'):  # GPG fp/key submitted
            return True
        elif site.get('GPG_FINGERPRINT') and settings.FORCE_GPG_SIGNING:  # site has gpg and forced
            return True
        return False

    def msg_with_gpg(self, site, frm, subject, text, html, payload=None, quiet=True):
        """
        :param site: Matching dict from XMPP_HOSTS.
        :param text: The text part of the message.
        :param html: The HTML part of the message.
        :param quiet: If False, raise an Exception, the default is only to log errors.
        """
        if payload is None:
            payload = json.loads(self.payload)

        gpg = settings.GPG
        signer = site.get('GPG_FINGERPRINT')
        sign = False
        encrypt = False

        recipient = payload.get('email', self.user.email)
        gpg_fingerprint = payload.get('gpg_fingerprint')

        # encrypt only if the user has a fingerprint
        if gpg_fingerprint:
            # Receive key of recipient. We don't care about the result, because user might have
            # already uploaded it.
            gpg.recv_keys(settings.GPG_KEYSERVER, gpg_fingerprint)

            # ... instead, we check if it is a known key after importing
            if gpg_fingerprint not in [k['fingerprint'] for k in gpg.list_keys()]:
                if quiet is True:
                    log.warn('%s: Unknown GPG fingerprint for %s', site['DOMAIN'], self.user.jid)
                else:
                    raise GpgFingerprintError(_("GPG key not found on keyservers."))
            else:
                encrypt = True

        elif 'gpg_key' in payload:
            # No fingerprint but a gpg_key in the payload, so import the key. This should only be
            # happening if we're using Celery.
            log.warn('Importing gpg key in msg_with_gpg()')

            imported = settings.GPG.import_keys(payload['gpg_key'])
            if not imported.fingerprints:
                if quiet is True:
                    log.warn("No imported keys: %s\ndata: %s", imported.stderr, payload['gpg_key'])
                else:
                    raise GpgKeyError(_("GPG key could not be imported."))
            else:
                gpg_fingerprint = imported.fingerprints[0]
                payload['gpg_fingerprint'] = gpg_fingerprint
                encrypt = True

                # save the payload to make sure it will always have one during confirmation
                self.payload = json.dumps(payload)
                self.save()

        # sign only if the user has fingerprint or signing is forced
        if not signer:
            log.warn('%s: No GPG key configured, not signing', site['DOMAIN'])
        elif signer not in [k['fingerprint'] for k in gpg.list_keys(True)]:
            log.warn('%s: %s: secret key not found, not signing', site['DOMAIN'], signer)
            signer = None
        elif gpg and (gpg_fingerprint or settings.FORCE_GPG_SIGNING):
            sign = True

        log.info('sign, encrypt: %s/%s', sign, encrypt)
        if not (sign or encrypt):  # shortcut if no GPG is used
            return self.msg_without_gpg(subject, frm, recipient, text, html)

        msg = EmailMultiAlternatives(subject, from_email=frm, to=[recipient])
        mime_text = MIMEText(text, _charset='utf-8')
        mime_html = MIMEText(html, _subtype='html', _charset='utf-8')
        body = MIMEMultipart(_subtype='alternative', _subparts=[mime_text, mime_html])

        if sign and not encrypt:  # only sign the message
            signed_body = gpg.sign(body.as_string(), keyid=signer, detach=True)
            if not signed_body.data:
                if quiet is True:
                   log.warn('GPG returned no data when signing')
                   log.warn(signed_body.stderr)
                   return self.msg_without_gpg(subject, frm, recipient, text, html)
                else:
                   raise GpgError("Error signing message: %s" % signed_body.stderr)

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
                if quiet is True:
                    log.warn('GPG returned no data when signing/encrypting')
                    log.warn(encrypted_body.stderr)
                    return self.msg_without_gpg(subject, frm, recipient, text, html)
                else:
                   raise GpgError("Error encrypting message: %s" % encrypted_body.stderr)

            encrypted = MIMEBase(_maintype='application', _subtype='octed-stream',
                                 name='encrypted.asc')
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

    def msg_without_gpg(self, subject, frm, recipient, text, html):
        msg = EmailMultiAlternatives(subject, from_email=frm, to=[recipient])
        msg.body = text
        msg.attach_alternative(html, 'text/html')
        return msg

    def get_msg_data(self, payload, uri, site, lang):
        frm = site.get('FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        recipient = payload.get('email', self.user.email)

        subject = PURPOSES[self.purpose]['subject'] % {
            'domain': self.user.domain,
        }
        context = {
            'username': self.user.node,
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

        return frm, recipient, subject, text, html

    def send(self, uri, site, lang):
        """Send this confirmation key.

        This method is intended to be used inside the WSGI daemon if celery is not used.
        """
        payload = json.loads(self.payload)
        frm, recipient, subject, text, html = self.get_msg_data(payload, uri, site, lang)

        if self.should_use_gpg(payload, site):
            with GpgLock():
                msg = self.msg_with_gpg(site, frm, subject, text, html, payload=payload,
                                        quiet=False)
        else:
            msg = self.msg_without_gpg(subject, frm, recipient, text, html)

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
    purpose = models.CharField(max_length=12, choices=NEW_PURPOSE_CHOICES)

    class Meta:
        verbose_name = _('IP-Address Activity')
        verbose_name_plural = _('IP-Address Activities')

    def __str__(self):
        return '%s: %s/%s' % (PURPOSE_DICT[self.purpose], self.address.address,
                              self.user.jid)
