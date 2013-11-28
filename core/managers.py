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

from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils.crypto import salted_hmac

from core.querysets import ConfirmationQuerySet
from core.utils import random_string


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
        return ConfirmationQuerySet(self.model)

    def create(self, user, purpose, key=None, **kwargs):
        if key is None:
            salt = random_string()
            value = '%s-%s-%s' % (user.email, user.username, user.domain)
            key = salted_hmac(salt, value).hexdigest()
        return super(ConfirmationManager, self).create(
            user=user, purpose=purpose, key=key, **kwargs)

    def valid(self):
        return self.get_query_set().valid()

    def registrations(self):
        return self.get_query_set().registrations()

    def passwords(self):
        return self.get_query_set().passwords()

    def emails(self):
        return self.get_query_set().emails()
