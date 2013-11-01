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

from subprocess import PIPE
from subprocess import Popen

from backends.base import UserExists
from backends.base import UserNotFound
from backends.base import BackendError
from backends.base import XmppBackendBase

class EjabberdctlBackend(XmppBackendBase):
    """Base class for all XMPP backends."""

    def ex(self, *cmd):
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        return p.returncode, stdout, stderr

    def ctl(self, *cmd):
        return self.ex('/usr/sbin/ejabberdctl', *cmd)

    def create(self, username, domain, password, email):
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
        if password is None:
            password = self.get_random_password()

        elif settings.XMPP_HOSTS[domain].get('RESERVE', False):
            self.set_password(username, domain, password)
            self.set_email(username, domain, email)
            return

        code, out, err = self.ctl('register', username, domain, password)

        if code == 0:
            return
        elif code == 1:
            raise UserExists()
        else:
            raise BackendError(code)

    def check_password(self, username, domain, password):
        """Check the password of a user.

        :param username: The username of the new user.
        :param   domain: The selected domain, may be any domain provided
                         in :ref:`settings-XMPP_HOSTS`.
        :param password: The password to check.
        :return: ``True`` if the password is correct, ``False`` otherwise.
        """
        code, out, err = self.ctl('check_password', username, domain, password)

        if code == 0:
            return True
        elif code == 1:
            return False
        else:
            raise BackendError()

    def set_password(self, username, domain, password):
        """Set the password of a user.

        :param username: The username of the new user.
        :param   domain: The selected domain, may be any domain provided
                         in :ref:`settings-XMPP_HOSTS`.
        :param password: The password to set.
        """
        code, out, err = self.ctl('change_password', username, domain,
                                  password)
        if code != 0:  # 0 is also returned if the user doesn't exist.
            raise BackendError()

    def set_unusable_password(self, username, domain):
        code, out, err = self.ctl('ban_account', username, domain,
                                  'by django-xmpp-account')
        if code != 0:
            raise BackendError()

    def has_usable_password(self, username, domain):
        return True  # unfortunately we can't tell

    def set_email(self, username, domain, email):
        # ejabberdctl get_vcard2 mati jabber.at EMAIL USERID
        pass  # maybe as vcard field?

    def check_email(self, username, domain, email):
        pass  # maybe as vcard field?

    def remove(self, username, domain):
        """Remove a user.

        This method is called when a confirmation key expires or when the user
        explicitly wants to remove her/his account.

        :param username: The username of the new user.
        :param     domain: The domainname selected, may be any domainname provided
                         in :ref:`settings-XMPP_HOSTS`.
        """
        code, out, err = self.ctl('unregister', username, domain)
        if code != 0:  # 0 is also returned if the user does not exist
            raise BackendError()
