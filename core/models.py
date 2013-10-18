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

from django.conf import settings
from django.db import models

from django.contrib.auth.models import AbstractBaseUser

from core.managers import RegistrationUserManager


class RegistrationUser(AbstractBaseUser):
    username = models.CharField(max_length=1023, unique=True)
    domain = models.CharField(
        max_length=253,
        choices=tuple([(host, host) for host in settings.XMPP_HOSTS])
    )  # maximum length of a domain name is 253 characters (according to spec)
    email = models.EmailField(unique=True)

    # when the account was first registered
    registered = models.DateTimeField(auto_now_add=True)
    # when the email was confirmed
    confirmed = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = RegistrationUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'domain', ]

    class Meta:
        unique_together = (
            ('username', 'domain', ),
        )

    @property
    def jid(self):
        return '%s@%s' % (self.username, self.domain)

    def __unicode__(self):
        return self.email

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
