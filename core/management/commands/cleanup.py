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
from datetime import timedelta

import pytz

from django.conf import settings
from django.core.management.base import BaseCommand

from core.models import Confirmation
from core.models import UserAddresses


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = pytz.utc.localize(datetime.now())

        # delete old addresses:
        stamp = now - timedelta(days=31)
        UserAddresses.objects.filter(timestamp__lt=stamp).delete()

        # delete old confirmation keys:
        Confirmation.objects.expired().delete()
