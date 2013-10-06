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

    def create(self, username, host, password, email):
        """Create a new user.

        .. NOTE:: The password this method receives is randomly generated and
           is not the one provided by the user. This method actually only
           "reserves" the username so no one else can create a user with the
           same name.

        :param username: The username of the new user.
        :param     host: The hostname selected, may be any hostname provided
                         in :ref:`settings-XMPP_HOSTS`.
        :param password: A randomly generated password.
        :param    email: The email address provided by the user.
        """
        raise NotImplementedError

    def check_password(self, username, host, password):
        """Check the password of a user.

        :param username: The username of the new user.
        :param     host: The hostname selected, may be any hostname provided
                         in :ref:`settings-XMPP_HOSTS`.
        :param password: The password to check.
        :return: ``True`` if the password is correct, ``False`` otherwise.
        """
        raise NotImplementedError

    def set_password(self, username, host, password):
        """Set the password of a user.

        :param username: The username of the new user.
        :param     host: The hostname selected, may be any hostname provided
                         in :ref:`settings-XMPP_HOSTS`.
        :param password: The password to set.
        """
        raise NotImplementedError

    def set_email(self, username, host, email):
        raise NotImplementedError

    def check_email(self, username, host, email):
        raise NotImplementedError

    def remove(self, username, host):
        """Remove a user.

        This method is called when a confirmation key expires or when the user
        explicitly wants to remove her/his account.

        :param username: The username of the new user.
        :param     host: The hostname selected, may be any hostname provided
                         in :ref:`settings-XMPP_HOSTS`.
        """
        raise NotImplementedError
