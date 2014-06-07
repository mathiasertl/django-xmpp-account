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

import time

from django.conf import settings

from core import xmlrpclib

from backends.base import XmppBackendBase
from backends.base import BackendError
from backends.base import UserExists


class EjabberdXMLRPCBackend(XmppBackendBase):
    """This backend uses the Ejabberd XMLRPC interface.

    This backend requires ejabberd mod_admin_extra to be installed.

    Example::

        XMPP_BACKENDS = {
            'default': {
                'BACKEND': 'backends.ejabberd_xmlrpc.EjabberdXMLRPCBackend',
                # optional:
                #'HOST': 'http:///127.0.0.1:4560',
                # optional, only if access is restricted in ejabberd config!
                #'USER': 'account',
                #'SERVER': 'jabber.at',
                #'PASSWORD': 'super-secure-password',
            },
        }

    This backend uses the following settings:

    **HOST** (optional, default:: ``http:///127.0.0.1:4560``)
        The host to connect to.
    **USER** (optional)
        The username of user used in the XMLRCP connection. Only use this
        setting if you actually restricted access in the ejabberd config!
    **SERVER** (optional)
        The server of the user used in the XMLRPC connection. Only use this
        setting if you actually restricted access in the ejabberd config!
    **PASSWORD** (optional)
        The password of the user used in the XMLRPC connection. Only use this
        setting if you actually restricted access in the ejabberd config!
    """
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
        if password is None:
            password = self.get_random_password()

        elif settings.XMPP_HOSTS[domain].get('RESERVE', False):
            self.set_password(username, domain, password)
            self.set_email(username, domain, email)
            return

        result = self.rpc('register', user=username, host=domain,
                          password=password)
        if result['res'] == 0:
            # set last activity, so that no user has the activity 'Never'.
            # this way the account isn't removed with delete_old_users.
            self.rpc('set_last', user=username, host=domain,
                     timestamp=int(time.time()), status='Registered')

            return
        elif result['res'] == 1:
            raise UserExists()
        else:
            raise BackendError(result.get('text', 'Unknown Error'))

    def check_password(self, username, domain, password):
        result = self.rpc('check_password', user=username, host=domain,
                          password=password)
        if result['res'] == 0:
            return True
        elif result['res'] == 1:
            return False
        else:
            raise BackendError(result.get('text', 'Unknown Error'))

    def set_password(self, username, domain, password):
        result = self.rpc('change_password', user=username, host=domain,
                          newpass=password)
        if result['res'] == 0:
            return True
        else:
            raise BackendError(result.get('text', 'Unknown Error'))

    def has_usable_password(self, username, domain):
        return True

    def set_email(self, username, domain, email):
        """Not yet implemented."""
        pass

    def check_email(self, username, domain, email):
        """Not yet implemented."""
        pass

    def remove(self, username, domain):
        result = self.rpc('unregister', user=username, host=domain)
        if result['res'] == 0:
            return True
        else:
            raise BackendError(result.get('text', 'Unknown Error'))
