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

from backends.base import XmppBackendBase
from backends.base import UserExists
from backends.base import UserNotFound

log = logging.getLogger(__name__)


class DummyBackend(XmppBackendBase):
    _users = {}

    def create(self, username, host, email):
        user = '%s@%s' % (username, host)
        password = self.get_random_password
        log.debug('Create user: %s (%s)', user, self.get_random_password())

        if user in self._users:
            raise UserExists
        else:
            self._users[user] = {
                'pass': password,
                'email': email,
            }

    def check_password(self, username, host, password):
        user = '%s@%s' % (username, host)
        log.debug('Check pass: %s -> %s', user, password)

        if user not in self._users:
            return False
        else:
            return self._users[user]['pass'] == password

    def check_email(self, username, host, email):
        user = '%s@%s' % (username, host)
        log.debug('Check email: %s --> %s', user, email)

        if user not in self._users:
            return False
        else:
            return self._users[user]['email'] == email

    def set_password(self, username, host, password):
        user = '%s@%s' % (username, host)
        log.debug('Set pass: %s -> %s', user, password)

        if user not in self._users:
            raise UserNotFound
        else:
            self._users[user]['pass'] = password

    def set_email(self, username, host, email):
        user = '%s@%s' % (username, host)
        log.debug('Set email: %s --> %s', user, email)

        if user not in self._users:
            raise UserNotFound
        else:
            self._users[user]['email'] = email

    def remove(self, username, host):
        user = '%s@%s' % (username, host)
        log.debug('Remove: %s (%s)', user)

        if user not in self._users:
            raise UserNotFound
        else:
            del self._users[user]
