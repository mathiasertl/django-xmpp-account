# -*- coding: utf-8 -*-
#
# This file is part of xmppregister (https://account.jabber.at/doc).
#
# xmppregister is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xmppregister is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xmppregister.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from django.db import models

from core.querysets import ConfirmationQuerySet


class RegistrationUserManager(BaseUserManager):
    def create_user(self, email, username, domain, password=None):
        """Create a user.

        .. NOTE:: Password is required by manage.py createuser but is unused.
        """
        user = self.model(email=email, username=username, domain=domain)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, username, domain, password=None):
        """Create a superuser.

        .. NOTE:: Password is required by manage.py createuser but is unused.
        """
        user = self.model(email=email, username=username, domain=domain,
                          is_admin=True)
        user.save(using=self.db)
        return user

class ConfirmationManager(models.Manager):
    def get_query_set(self):
        timestamp = datetime.now() - settings.CONFIRMATION_TIMEOUT
        return ConfirmationQuerySet(self.model).filter(created__gt=timestamp)

    def registrations(self):
        return self.get_query_set().registrations()

    def passwords(self):
        return self.get_query_set().passwords()

    def emails(self):
        return self.get_query_set().emails()
