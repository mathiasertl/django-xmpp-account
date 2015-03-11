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
from django.utils import six
from django.utils.translation import ugettext_lazy as _

if six.PY2:
    from core import xmlrpclib
else:  # py3
    from xmlrpc import client as xmlrpclib
from core.exceptions import TemporaryError

from backends.base import XmppBackendBase
from backends.base import BackendError
from backends.base import UserExists


class EjabberdXMLRPCBackend(XmppBackendBase):
    """This backend uses the Ejabberd XMLRPC interface.

    This backend requires ejabberd mod_admin_extra to be installed.

    .. WARNING:: The encoding of UTF8 characters differs in ejabberd <= 14.07. Set the
        `UTF8_ENCODING` option to `php` if you use any of these versions.

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
        The username of user used in the XMLRCP connection. Only use this setting if you actually
        restricted access in the ejabberd config!
    **SERVER** (optional)
        The server of the user used in the XMLRPC connection. Only use this setting if you actually
        restricted access in the ejabberd config!
    **PASSWORD** (optional)
        The password of the user used in the XMLRPC connection. Only use this setting if you
        actually restricted access in the ejabberd config!
    **UTF8_ENCODING** (optional)
        How to encode UTF8 characters. Set to 'php' for ejabberd <= 14.05. Currently only used for
        Python 2.

    **ejabberd configuration:** The ``xmlrpc`` module is included with ejabberd_ since version
    13.12. If you use an earlier version, please get and run the module from the
    ``ejabberd-contrib`` repository. Configuring the interface is simple::

        listen:
            - ip: "127.0.0.1"
              port: 4560
              module: ejabberd_xmlrpc
    """
    credentials = None

    def __init__(self, HOST='http://127.0.0.1:4560', USER=None, SERVER=None, PASSWORD=None,
                 UTF8_ENCODING='standard'):
        super(EjabberdXMLRPCBackend, self).__init__()

        kwargs = {}
        if six.PY2:
            kwargs['utf8_encoding'] = UTF8_ENCODING
        if settings.DEBUG:
            kwargs['verbose'] = True

        self.client = xmlrpclib.ServerProxy(HOST, **kwargs)
        if USER is not None:
            self.credentials = {
                'user': USER,
                'server': SERVER,
                'password': PASSWORD,
            }

    def rpc(self, cmd, **kwargs):
        func = getattr(self.client, cmd)
        try:
            if self.credentials is None:
                return func(kwargs)
            else:
                return func(self.credentials, kwargs)
        except xmlrpclib.ProtocolError:
            raise TemporaryError(_("Our server is experiencing temporary difficulties. "
                                   "Please try again later."))

    def create(self, username, domain, password, email):
        if password is None:
            password = self.get_random_password()

        elif settings.XMPP_HOSTS[domain].get('RESERVE', False):
            self.set_password(username, domain, password)
            self.set_email(username, domain, email)
            return

        result = self.rpc('register', user=username, host=domain, password=password)
        if result['res'] == 0:
            # set last activity, so that no user has the activity 'Never'. This way the account
            # isn't removed with delete_old_users.
            self.rpc('set_last', user=username, host=domain, timestamp=int(time.time()),
                     status='Registered')

            return
        elif result['res'] == 1:
            raise UserExists()
        else:
            raise BackendError(result.get('text', 'Unknown Error'))

    def exists(self, username, domain):
        return self.rpc('check_account', user=username, host=domain)

    def check_password(self, username, domain, password):
        result = self.rpc('check_password', user=username, host=domain, password=password)
        if result['res'] == 0:
            return True
        elif result['res'] == 1:
            return False
        else:
            raise BackendError(result.get('text', 'Unknown Error'))

    def set_password(self, username, domain, password):
        result = self.rpc('change_password', user=username, host=domain, newpass=password)
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

    def message(self, username, domain, subject, message):
        """Currently use send_message_chat and discard subject, because headline messages are not
        stored by mod_offline."""

        kwargs = {
            'body': message,
            'from': domain,
            'subject': subject,
            'to': '%s@%s' % (username, domain),
            'type': 'normal',
        }
        self.rpc('send_message', **kwargs)

    def all_users(self, domain):
        users = self.rpc('registered_users', host=domain)['users']
        return set([e['username'] for e in users])

    def remove(self, username, domain):
        result = self.rpc('unregister', user=username, host=domain)
        if result['res'] == 0:
            return True
        else:
            raise BackendError(result.get('text', 'Unknown Error'))
