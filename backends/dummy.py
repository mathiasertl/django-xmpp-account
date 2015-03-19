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

import logging

from django.conf import settings
from django.core.cache import cache

from backends.base import XmppBackendBase
from backends.base import UserExists
from backends.base import UserNotFound

log = logging.getLogger(__name__)


class DummyBackend(XmppBackendBase):
    """A dummy backend for development using Djangos caching framework.

    By default, Djangos caching framework uses in-memory data structures, so
    every registration will be removed if you restart the development server.
    You can configure a different cache (e.g. memcached), see
    `Django's cache framework <https://docs.djangoproject.com/en/dev/topics/cache/>`_
    for details.
    """

    def exists(self, username, domain):
        user = '%s@%s' % (username, domain)
        return cache.get(user) is not None

    def create(self, username, domain, password, email):
        if password is None:
            password = self.get_random_password()
        elif settings.XMPP_HOSTS[domain].get('RESERVE', False):
            self.set_password(username, domain, password)
            self.set_email(username, domain, email)
            return

        user = '%s@%s' % (username, domain)
        log.debug('Create user: %s (%s)', user, password)

        data = cache.get(user)
        if data is None:
            cache.set(user, {
                'pass': password,
                'email': email,
            })
        else:
            raise UserExists()

    def check_password(self, username, domain, password):
        user = '%s@%s' % (username, domain)
        log.debug('Check pass: %s -> %s', user, password)
        return True

        data = cache.get(user)
        if data is None:
            return False
        else:
            return data['pass'] == password

    def check_email(self, username, domain, email):
        user = '%s@%s' % (username, domain)
        log.debug('Check email: %s --> %s', user, email)

        data = cache.get(user)
        if data is None:
            return False
        else:
            return data['email'] == email

    def set_password(self, username, domain, password):
        user = '%s@%s' % (username, domain)
        log.debug('Set pass: %s -> %s', user, password)

        data = cache.get(user)
        if data is None:
            raise UserNotFound()
        else:
            data['pass'] = password
            cache.set(user, data)

    def set_email(self, username, domain, email):
        user = '%s@%s' % (username, domain)
        log.debug('Set email: %s --> %s', user, email)

        data = cache.get(user)
        if data is None:
            raise UserNotFound()
        else:
            data['email'] = email
            cache.set(user, data)

    def all_users(self, domain):
        return set()

    def remove(self, username, domain):
        user = '%s@%s' % (username, domain)
        log.debug('Remove: %s', user)

        cache.delete(user)
