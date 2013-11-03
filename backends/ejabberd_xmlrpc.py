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

import xmlrpclib

from django.conf import settings

from backends.base import XmppBackendBase
from backends.base import BackendError
from backends.base import UserExists


class EjabberdXMLRPCBackend(XmppBackendBase):
    credentials = None

    def __init__(self, HOST='http://127.0.0.1:4560', USER=None, SERVER=None,
                 PASSWORD=None):
        super(EjabberdXMLRPCBackend, self).__init__()

        self.client = xmlrpclib.ServerProxy(HOST)
        if USER is not None:
            self.credentials = {
                'user': USER,
                'server': SERVER,
                'password': PASSWORD,
            }

    def rpc(self, cmd, **kwargs):
        func = getattr(self.client, cmd)
        if self.credentials is None:
            return func(kwargs)
        else:
            return func(self.credentials, kwargs)

    def create(self, username, domain, password, email):
        """Create a new user.

        If the domains ``RESERVE`` setting is True and your backend does not
        override :py:func:`reserve`, then the password is ``None`` if this
        function is called via :py:func:`reserve`, in which case you can use
        :py:func:`get_random_password` for a password. If the password is not
        ``None, you have to consider that the user already exists (with a
        random password) in the backend and you only have to set his/her email
        and password::

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

                    # actually create teh user in the backend
                    self._really_create(username, domain, password, email)

        After this method, the user should be able to log in via XMPP.

        :param    username: The username of the new user.
        :param      domain: The selected domain, may be any domain provided
                            in :ref:`settings-XMPP_HOSTS`.
        :param    password: The password of the new user.
        :param       email: The email address provided by the user. Note that at
                            this point it is not confirmed. You are free to ignore
                            this parameter.
        :param reservation: True only when called via :py:func:`reserve`.
        """
        if password is None:
            password = self.get_random_password()

        elif settings.XMPP_HOSTS[domain].get('RESERVE', False):
            self.set_password(username, domain, password)
            self.set_email(username, domain, email)
            return

        result = self.rpc('register', user=username, host=domain,
                          password=password)
        if result['res'] == 0:
            return
        elif result['res'] == 1:
            raise UserExists()
        else:
            raise BackendError(result.get('text', 'Unknown Error'))

    def check_password(self, username, domain, password):
        """Check the password of a user.

        :param username: The username of the new user.
        :param   domain: The selected domain, may be any domain provided
                         in :ref:`settings-XMPP_HOSTS`.
        :param password: The password to check.
        :return: ``True`` if the password is correct, ``False`` otherwise.
        """
        result = self.rpc('check_password', user=username, host=domain,
                          password=password)
        if result['res'] == 0:
            return True
        elif result['res'] == 1:
            return False
        else:
            raise BackendError(result.get('text', 'Unknown Error'))

    def set_password(self, username, domain, password):
        """Set the password of a user.

        :param username: The username of the new user.
        :param   domain: The selected domain, may be any domain provided
                         in :ref:`settings-XMPP_HOSTS`.
        :param password: The password to set.
        """
        result = self.rpc('change_password', user=username, host=domain,
                          password=password)
        if result['res'] == 0:
            return True
        else:
            raise BackendError(result.get('text', 'Unknown Error'))

    def has_usable_password(self, username, domain):
        return True

    def set_email(self, username, domain, email):
        """Set the email address of a user."""
        pass

    def check_email(self, username, domain, email):
        """Check the email address of a user."""
        pass


    def remove(self, username, domain):
        """Remove a user.

        This method is called when the user explicitly wants to remove her/his
        account.

        :param username: The username of the new user.
        :param   domain: The domainname selected, may be any domainname
                         provided in :ref:`settings-XMPP_HOSTS`.
        """
        result = self.rpc('unregister', user=username, host=domain)
        if result['res'] == 0:
            return True
        else:
            raise BackendError(result.get('text', 'Unknown Error'))
