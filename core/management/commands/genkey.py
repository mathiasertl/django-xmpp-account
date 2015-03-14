# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-register (https://account.jabber.at/doc).
#
# django-xmpp-register is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# django-xmpp-register is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# django-xmpp-register.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import os

from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):
    help = "Generate GnuPG key for a host given in XMPP_HOSTS in localsettings.py."
    args = "<xmpp-host>"

    option_list = BaseCommand.option_list + (
        make_option(
            '--key-type', default='RSA', metavar='[DSA|RSA]',
            help='The type of primary key to generate (default: %default).'),
        make_option('--key-length', default=4096, type="int", metavar='BITS',
                    help='The length of the primary key (default: %default).'),
        make_option('--name', help="Override the real name (default: the xmpp-host used."),
        make_option('-f', '--force', action='store_true', default=False,
                    help="Force regeneration of GPG key."),
        make_option('-q', '--quiet', action='store_true', default=False,
                    help="Do not output deleted users."),
    )

    def handle(self, host, **kwargs):
        if settings.GNUPG is None:
            raise CommandError('GnuPG disabled by "GNUPG = None" in localsettings.py.')
        if host not in settings.XMPP_HOSTS:
            raise CommandError('%s: Host not named in XMPP_HOSTS setting.' % host)

        if not os.path.exists(settings.GNUPG['gnupghome']):
            os.makedirs(settings.GNUPG['gnupghome'], 0700)
        gpg = settings.GPG  # just a nice shortcut

        fingerprint = settings.XMPP_HOSTS.get('GPG_FINGERPRINT')
        secret_keys = gpg.list_keys(secret=True)
        secret_fps = [k['fingerprint'] for k in secret_keys]

        if fingerprint and fingerprint in secret_fps and not kwargs['force']:
            raise CommandError('Fingerprint set and found, use --force to force regenration.')

        if kwargs['name'] is None:
            kwargs['name'] = host
        email = settings.XMPP_HOSTS[host].get('FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)
        self.stdout.write('Generating key for %s <%s>... (takes a long time!)' % (host, email))

        params = gpg.gen_key_input(
            key_length=kwargs['key_length'],
            key_type=kwargs['key_type'],
            name_real=kwargs['name'],
            name_comment='',
            name_email=email
        )
        key = gpg.gen_key(params)
        if key.fingerprint:
            self.stdout.write(
                'Fingerprint is "%s", add as "GPG_FINGERPRINT" to the XMPP_HOSTS entry.' %
                key.fingerprint)
        else:
            raise CommandError('Cannot generate key, gpg output was: %s' % gpg.stderr)
