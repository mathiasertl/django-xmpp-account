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

import pytz

from django.conf import settings
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.crypto import salted_hmac

from core.constants import REGISTRATION_WEBSITE as WEBSITE
from core.querysets import ConfirmationQuerySet
from core.querysets import RegistrationUserQuerySet

tzinfo = pytz.timezone(settings.TIME_ZONE)


class RegistrationUserManager(BaseUserManager):
    def get_queryset(self):
        return RegistrationUserQuerySet(self.model)

    def get_user(self, username, domain):
        return self.get_queryset().get_user(username, domain)

    def has_email(self):
        return self.get_queryset().has_email()

    def create_user(self, jid, email, password=None):
        """Create a user.

        .. NOTE:: Password is required by manage.py createuser but is unused.
        """
        now = tzinfo.localize(datetime.now())
        name, domain = jid.split('@')
        user = self.model(username=name, domain=domain, email=email, confirmed=now,
                          registration_method=WEBSITE)
        user.save(using=self.db)
        return user

    def create_superuser(self, jid, email, password=None):
        """Create a superuser.

        .. NOTE:: Password is required by manage.py createuser but is unused.
        """
        now = tzinfo.localize(datetime.now())
        name, domain = jid.split('@')
        user = self.model(username=name, domain=domain, email=email, confirmed=now,
                          registration_method=WEBSITE, is_admin=True)
        user.save(using=self.db)
        return user


class ConfirmationManager(models.Manager):
    def get_queryset(self):
        return ConfirmationQuerySet(self.model)

    def create(self, user, purpose, key=None, **kwargs):
        if key is None:
            salt = get_random_string(32)
            value = '%s-%s-%s' % (user.email, user.node, user.domain)
            key = salted_hmac(salt, value).hexdigest()
        return super(ConfirmationManager, self).create(
            user=user, purpose=purpose, key=key, **kwargs)
