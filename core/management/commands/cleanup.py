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

from datetime import datetime
from datetime import timedelta

import pytz

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from django_xmpp_backends import backend

from core.constants import REGISTRATION_WEBSITE
from core.models import Confirmation
from core.models import UserAddresses

User = get_user_model()
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
log = logging.getLogger('cleanup')  # we log to a file

_default_timeout_delta = getattr(settings, 'DJANGO_CONFIRM_DEFAULT_TIMEOUT', timedelta(hours=24))


class Command(BaseCommand):
    def add_argument(self, parser):
        parser.add_argument('-q', '--quiet', action='store_true', default=False,
                            help="Do not output deleted users."),

    def handle(self, *args, **kwargs):
        if kwargs.get('quiet'):
            log.setLevel('WARN')

        now = pytz.utc.localize(datetime.now())

        # delete old addresses:
        stamp = now - timedelta(days=31)
        UserAddresses.objects.filter(timestamp__lt=stamp).delete()

        # delete old confirmation keys:
        Confirmation.objects.expired().delete()
        expired_timestamp = datetime.now() - timedelta(days=3)

        for domain, config in settings.XMPP_HOSTS.items():
            # lowercase usernames from backend just to be sure
            existing_users = set([u.lower() for u in backend.all_users(domain)])

            if len(existing_users) < 100:
                # A silent safety check if the backend for some reason does not return any users
                # and does not raise an exception.
                log.warn('Skipping %s: Only %s users received.', domain, len(existing_users))
                continue

            # only consider users that have no pending confirmation keys
            created_before = timezone.now() - _default_timeout_delta
            users = User.objects.filter(jid__endswith='@%s' % domain, registered__lt=created_before)

            for user in users:
                username = user.node.lower()
                if username not in existing_users:
                    log.info('%s: Removed from database (gone from backend)', username)
                    user.delete()

            if not config.get('RESERVE', False):
                continue

            expired = users.filter(registration_method=REGISTRATION_WEBSITE,
                                   confirmed__isnull=True, registered__lt=expired_timestamp)
            for user in expired:
                username = user.node.lower()
                log.info('%s: Registration expired', username)
                backend.expire_reservation(username, user.domain)
            if len(expired) > 10:
                # warn, if many users were removed
                log.warn('Removed %s users', len(expired))
            expired.delete()
