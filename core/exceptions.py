# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-register (https://account.jabber.at/doc).
#
# django-xmpp-register is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# django-xmpp-register is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# django-xmpp-register.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals


class SpamException(Exception):
    """Raised whenever we detect behaviour that suggests a spam-bot."""
    pass


class RateException(Exception):
    """Raised when the user views/posts too often."""
    pass


class TemporaryError(Exception):
    """Raised when a temporary error occurs."""
    pass


class RegistrationRateException(RateException):
    """Raised when the user exceeds rate for registrations."""


class GpgError(Exception):
    """Raised when generally handling GPG."""
    field = None

class GpgFingerprintError(GpgError):
    """Raised when handling (e.g. fetching) fingerprints."""
    field = 'fingerprint'


class GpgKeyError(GpgError):
    """Raised when e.g. importing raw GPG keys."""
    field = 'gpg_key'
