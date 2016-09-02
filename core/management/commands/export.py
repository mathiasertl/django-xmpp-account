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

import codecs
import logging
import sys

from datetime import timedelta

import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
log = logging.getLogger('cleanup')  # we log to a file

_default_timeout_delta = getattr(settings, 'DJANGO_CONFIRM_DEFAULT_TIMEOUT', timedelta(hours=24))


class Command(BaseCommand):
    def add_argument(self, parser):
        parser.add_argument('-q', '--quiet', action='store_true', default=False,
                            help="Do not output deleted users."),

    def handle(self, *args, **kwargs):
        timeformat = '%Y-%m-%d %H:%M:%S'
        data = []
        for user in User.objects.all():
            userdata = {
                'username': user.jid,
                'email': user.email,
                'registered': user.registered.strftime(timeformat),
                'registration_method': user.registration_method,
            }
            if user.confirmed is not None:
                userdata['confirmed'] = user.confirmed.strftime(timeformat)
            if user.gpg_fingerprint is not None:
                key = settings.GPG.export_keys([user.gpg_fingerprint])
            if user.gpg_fingerprint is not None:
                key = settings.GPG.export_keys([user.gpg_fingerprint])
                if key:
                    userdata['gpg_fingerprint'] = user.gpg_fingerprint
                    userdata['gpg_key'] = key
            data.append(userdata)
        self.stdout.write(json.dumps(data, indent=4))
