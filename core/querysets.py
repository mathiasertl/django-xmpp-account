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

from datetime import datetime

from django.conf import settings

import pytz

from django.db.models.query import QuerySet
from django.db.models.query_utils import Q

from core.constants import PURPOSE_REGISTER
from core.constants import PURPOSE_SET_PASSWORD
from core.constants import PURPOSE_SET_EMAIL


class RegistrationUserQuerySet(QuerySet):
    def has_email(self):
        #if not self.email or not self.confirmed:
        return self.exclude(Q(email__isnull=True) | Q(confirmed__isnull=True))


class ConfirmationQuerySet(QuerySet):
    @property
    def timestamp(self):
        return pytz.utc.localize(datetime.now()) - settings.CONFIRMATION_TIMEOUT

    def valid(self):
        return self.filter(created__gt=self.timestamp)

    def expired(self):
        return self.filter(created__lt=self.timestamp)

    def purpose(self, purpose):
        return self.filter(purpose=purpose)

    def registrations(self):
        return self.filter(purpose=PURPOSE_REGISTER)

    def passwords(self):
        return self.filter(purpose=PURPOSE_SET_PASSWORD)

    def emails(self):
        return self.filter(purpose=PURPOSE_SET_EMAIL)
