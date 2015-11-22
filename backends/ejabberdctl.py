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
import warnings

from django.conf import settings

from subprocess import PIPE
from subprocess import Popen

from backends.base import UserExists
from backends.base import BackendError
from backends.base import XmppBackendBase

warnings.warn('This module is deprecated, please use "xmpp_backends.ejabberdctl" instead.',
              DeprecationWarning)


class EjabberdctlBackend(XmppBackendBase):
    """This backend uses the ejabberdctl command line utility.

    This backend requires ejabberd mod_admin_extra to be installed.

    Example::

        XMPP_BACKENDS = {
            'BACKEND': 'backends.ejabberdctl.EjabberdctlBackend',
            # optional:
            #'EJABBERDCTL_PATH': '/usr/sbin/ejabberdctl',
        }

    .. WARNING:: This backend is not very secure because ejabberdctl gets any
       passwords in clear text via the commandline. The process list (and thus
       the passwords) can usually be viewed by anyone that has shell-access to
       your machine!

    This backend uses the following settings:

    **EJABBERDCTL_PATH** (optional, default: :file:`/usr/sbin/ejabberdctl`)
        The full path to the ejabberdctl utility.
    """

    def __init__(self, EJABBERDCTL_PATH='/usr/sbin/ejabberdctl'):
        self.ejabberdctl = EJABBERDCTL_PATH

    def ex(self, *cmd):
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        return p.returncode, stdout, stderr

    def ctl(self, *cmd):
        return self.ex(self.ejabberdctl, *cmd)

    def create(self, username, domain, password, email):
        if password is None:
            password = self.get_random_password()

        elif settings.XMPP_HOSTS[domain].get('RESERVE', False):
            self.set_password(username, domain, password)
            self.set_email(username, domain, email)
            return

        code, out, err = self.ctl('register', username, domain, password)

        if code == 0:
            self.ctl('set_last', username, domain, int(time.time()),
                     'Registered')
            return
        elif code == 1:
            raise UserExists()
        else:
            raise BackendError(code)  # TODO: 3 means nodedown.

    def check_password(self, username, domain, password):
        code, out, err = self.ctl('check_password', username, domain, password)

        if code == 0:
            return True
        elif code == 1:
            return False
        else:
            raise BackendError(code)

    def set_password(self, username, domain, password):
        code, out, err = self.ctl('change_password', username, domain,
                                  password)
        if code != 0:  # 0 is also returned if the user doesn't exist.
            raise BackendError(code)

    def set_unusable_password(self, username, domain):
        code, out, err = self.ctl('ban_account', username, domain,
                                  'by django-xmpp-account')
        if code != 0:
            raise BackendError(code)

    def has_usable_password(self, username, domain):
        return True  # unfortunately we can't tell

    def set_email(self, username, domain, email):
        """Not yet implemented."""
        # ejabberdctl get_vcard2 mati jabber.at EMAIL USERID
        pass  # maybe as vcard field?

    def check_email(self, username, domain, email):
        """Not yet implemented."""
        pass  # maybe as vcard field?

    def message(self, username, domain, subject, message):
        """Currently use send_message_chat and discard subject, because headline messages are not
        stored by mod_offline."""
        self.ctl('send_message_chat', domain, '%s@%s' % (username, domain), message)

    def all_users(self, domain):
        code, out, err = self.ctl('registered_users', domain)
        if code != 0:
            raise BackendError(code)

        return set(out.splitlines())


    def remove(self, username, domain):
        code, out, err = self.ctl('unregister', username, domain)
        if code != 0:  # 0 is also returned if the user does not exist
            raise BackendError(code)
