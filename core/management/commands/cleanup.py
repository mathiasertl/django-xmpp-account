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

import codecs
import sys

from datetime import datetime
from datetime import timedelta

import pytz

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from backends import backend
from core.constants import REGISTRATION_WEBSITE
from core.models import Confirmation
from core.models import UserAddresses

User = get_user_model()
sys.stdout = codecs.getwriter('utf8')(sys.stdout)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = pytz.utc.localize(datetime.now())

        # delete old addresses:
        stamp = now - timedelta(days=31)
        UserAddresses.objects.filter(timestamp__lt=stamp).delete()

        # delete old confirmation keys:
        Confirmation.objects.expired().delete()
        delete_unconfirmed_timestamp = datetime.now() - timedelta(days=3)

        for domain, config in settings.XMPP_HOSTS.items():
            # lowercase usernames from backend just to be sure
            existing_users = set([u.lower() for u in backend.all_users(domain)])

            if len(existing_users) < 100:
                # A silent safety check if the backend for some reason does not return any users
                # and does not raise an exception.
                continue

            # only consider users that have no pending confirmation keys
            users = User.objects.filter(domain=domain, confirmation__isnull=True)
            num_users = 0

            #for user in sorted([u.username.lower() for u in users]):
            for user in users:
                if user.username.lower() not in existing_users:
                    num_users += 1
                    user.delete()
            print("Deleted %s users on %s." % (num_users, domain))

            if not config.get('RESERVE', False):
                continue

            users = users.filter(registration_method=REGISTRATION_WEBSITE, confirmed__isnull=True,
                                 registered__lt=delete_unconfirmed_timestamp)
            for user in users:
                print('%s@%s: Removing (registration expired).' % (user.username.lower(), user.domain))
