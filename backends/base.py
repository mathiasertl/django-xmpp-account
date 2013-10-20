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

"""Common code for XMPP backends."""

from __future__ import unicode_literals

import random
import string

PASSWORD_CHARS = string.ascii_letters + string.digits


class InvalidXmppBackendError(Exception):
    """Raised when a backend is raised that cannot be imported."""
    pass


class UserExists(Exception):
    """Raised when a user already exists."""
    pass


class UserNotFound(Exception):
    """Raised when a user is not found."""
    pass


class XmppBackendBase(object):
    """Base class for all XMPP backends."""

    def get_random_password(self):
        return ''.join(random.choice(PASSWORD_CHARS) for x in range(16))

    def create(self, username, domain, email):
        """Create a new user.

        This method is invoked when a user first registers for an account. At
        this point, he/she does not have a confirmed email address and hasn't
        provided a password.

        If your backend requires you to set a password, you can use
        :py:func:`get_random_password` to get a random password.

        :param username: The username of the new user.
        :param   domain: The selected domain, may be any domain provided
                         in :ref:`settings-XMPP_HOSTS`.
        :param    email: The email address provided by the user. Note that at
                         this point it is not confirmed. You are free to ignore
                         this parameter.
        """
        raise NotImplementedError

    def check_password(self, username, domain, password):
        """Check the password of a user.

        :param username: The username of the new user.
        :param   domain: The selected domain, may be any domain provided
                         in :ref:`settings-XMPP_HOSTS`.
        :param password: The password to check.
        :return: ``True`` if the password is correct, ``False`` otherwise.
        """
        raise NotImplementedError

    def set_password(self, username, domain, password):
        """Set the password of a user.

        :param username: The username of the new user.
        :param   domain: The selected domain, may be any domain provided
                         in :ref:`settings-XMPP_HOSTS`.
        :param password: The password to set.
        """
        raise NotImplementedError

    def set_unusable_password(self, username, domain):
        self.set_password(username, domain, self.get_random_password())

    def has_usable_password(self, username, domain):
        return True

    def set_email(self, username, domain, email):
        raise NotImplementedError

    def check_email(self, username, domain, email):
        raise NotImplementedError

    def remove(self, username, domain):
        """Remove a user.

        This method is called when a confirmation key expires or when the user
        explicitly wants to remove her/his account.

        :param username: The username of the new user.
        :param     domain: The domainname selected, may be any domainname provided
                         in :ref:`settings-XMPP_HOSTS`.
        """
        raise NotImplementedError
