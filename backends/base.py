# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-register (https://account.jabber.at/doc).
#
# django-xmpp-register is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# django-xmpp-register is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# django-xmpp-register.  If not, see <http://www.gnu.org/licenses/>.

"""Common code for XMPP backends."""

from __future__ import unicode_literals

from django.utils import importlib

from core.utils import random_string


class BackendError(Exception):
    """All backend exceptions should be a subclass of this exception."""
    pass


class InvalidXmppBackendError(BackendError):
    """Raised when a backend is raised that cannot be imported."""
    pass


class UserExists(BackendError):
    """Raised when a user already exists."""
    pass


class UserNotFound(BackendError):
    """Raised when a user is not found."""
    pass


class XmppBackendBase(object):
    """Base class for all XMPP backends."""

    library = None
    """Import-party of any third-party library you need.

    Set this attribute to an import path and you will be able to access the module as
    ``self.module``. This way you don't have to do a module-level import, which would mean that
    everyone has to have that library installed, even if they're not using your backend.
    """
    _module = None

    @property
    def module(self):
        """The module specified by the ``library`` attribute."""

        if self._module is None:
            if self.library is None:
                raise ValueError(
                    "Backend '%s' doesn't specify a library attribute" % self.__class__)

            if isinstance(self.library, (tuple, list)):
                name, mod_path = self.library
            else:
                name = mod_path = self.library
            try:
                module = importlib.import_module(mod_path)
            except ImportError:
                raise ValueError("Couldn't load %s backend library library" % name)
            self._module = module
        return self._module

    def get_random_password(self, length=32):
        """Get a random password.

        :param length: The length of the random password.
        """
        return random_string(length=length)

    def exists(self, username, domain):
        """Return True if the user exists, false otherwise."""

        raise NotImplementedError

    def reserve(self, username, domain, email):
        """Reserve a new account.

        This method is called when the user first registers for an account on a domain with its
        ``RESERVE`` setting set to True (see :ref:`settings-XMPP_HOSTS`). The email address is not
        yet confirmed and the user hasn't provided a password yet, so login via XMPP should be
        impossible at this point.

        The default implementation calls :py:func:`~backends.base.XmppBackendBase.create` with
        password=None.  You can override this if your account supports a true "reservation" method
        that blocks registration via other means but does not allow the user to log in.

        :param username: The username of the new user.
        :param   domain: The selected domain, may be any domain provided
                         in :ref:`settings-XMPP_HOSTS`.
        :param    email: The email address provided by the user. Note that at this point it is not
                         confirmed. You are free to ignore this parameter.
        """
        self.create(username=username, domain=domain, password=None,
                    email=email)

    def create(self, username, domain, password, email):
        """Create a new user.

        If the domains ``RESERVE`` setting is ``True`` (see :ref:`settings-XMPP_BACKENDS`) and your
        backend does not override :py:func:`~backends.base.XmppBackendBase.reserve`, then the
        password is ``None`` if this function is called via
        :py:func:`~backends.base.XmppBackendBase.reserve`, in which case you can use
        :py:func:`~backends.base.XmppBackendBase.get_random_password` for a password. If the
        password is not ``None``, you have to consider that the user already exists (with a random
        password) in the backend and you only have to set his/her email and password::

            from django.conf import settings
            from backends.base import XmppBackendBase

            class YourBackend(XmppBackendBase):
                def create(self, username, domain, password, email):
                    if password is None:
                        password = self.get_random_password()

                    elif settings.XMPP_HOSTS[domain].get('RESERVE', False):
                        # RESERVE setting is true, user already exists
                        self.set_password(username, domain, password)
                        self.set_email(username, domain, email)
                        return  # our work is done

                    # actually create the user in the backend
                    self._really_create(username, domain, password, email)

        :param    username: The username of the new user.
        :param      domain: The selected domain, may be any domain provided
                            in :ref:`settings-XMPP_HOSTS`.
        :param    password: The password of the new user.
        :param       email: The email address provided by the user. Note that at this point it is
                            not confirmed. You are free to ignore this parameter.
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
        """Called when a user is blocked.

        The default implementation calls :py:func:`set_password` with a random password.
        """
        self.set_password(username, domain, self.get_random_password())

    def has_usable_password(self, username, domain):
        return True

    def set_email(self, username, domain, email):
        """Set the email address of a user."""
        raise NotImplementedError

    def check_email(self, username, domain, email):
        """Check the email address of a user."""
        raise NotImplementedError

    def expire(self, username, domain):
        """Expire a username reservation.

        This method is called when the confirmation key for a registration expires. The default
        implementation just calls :py:func:`~backends.base.XmppBackendBase.remove`. This is fine if
        you do not override :py:func:`~backends.base.XmppBackendBase.reserve`.
        """
        self.remove(username, domain)

    def message(self, username, domain, subject, message):
        """Send a message to the given user."""
        pass

    def all_users(self, domain):
        """Get all users for a given domain.

        :param   domain: The selected domain, may be any domain provided
                         in :ref:`settings-XMPP_HOSTS`.
        :returns: A set of all users.
        """
        raise NotImplementedError

    def remove(self, username, domain):
        """Remove a user.

        This method is called when the user explicitly wants to remove her/his account.

        :param username: The username of the new user.
        :param   domain: The domainname selected, may be any domainname
                         provided in :ref:`settings-XMPP_HOSTS`.
        """
        raise NotImplementedError
