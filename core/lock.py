# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-account (https://github.com/mathiasertl/django-xmpp-account/).
#
# django-xmpp-account is free software: you can redistribute it and/or modify it under the terms of
# the GNU General Public License as published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# django-xmpp-account is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with django-xmpp-account.
# If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, unicode_literals

import fcntl
import logging
import os

from django.conf import settings
from django.core.cache import caches

from redis.client import Redis

log = logging.getLogger(__name__)
cache = caches['default']


class FileLock(object):
    """A global (distributed) lock.

    This class should be used as a context manager. It currently supports using Redis for locking.
    A global Redis cache is recommended. If you have a Redis client as fallback, you can pass it as
    `cache_fallback`.

    If no Redis cache is configured and you do not pass a fallback, this class will fallback to
    `fcntl` (Unix only!). This will not work across multiple machines *but* is at least safe
    accross multiple processes.
    """

    def __init__(self, path, cache_fallback=None):
        self.path = '%s.xmppaccount.lock' % path
        self.cache = cache_fallback

        # TODO: Memcached caches should be suitable as well:
        # https://russellneufeld.wordpress.com/2012/05/24/using-memcached-as-a-distributed-lock-from-within-django/

        # Use one of the supported cache backends
        if cache.__module__ == 'django_redis.cache':
            self.use_redis(cache.client.get_client(True))

        # Try to use passed cache as fallback. This is only used when no suitable main cache is
        # found, because the main cache is shared between the WSGI server and Celery.
        elif isinstance(cache_fallback, Redis):
            log.warn('Using fallback cache, consider configuring a global Redis cache.')
            self.use_redis(cache_fallback)

        # Use fcntl (unix only!)
        else:  # TODO: Test here if we porperly support fcntl
            log.warn('Using fcntl locks, consider configuring a global Redis cache.')
            self.use_fcntl()

    def use_redis(self, client):
        self.client = client
        lock = self.client.lock(self.path, timeout=120)
        self.enter = lambda: lock.__enter__()
        self.exit = lambda exc_type, exc_value, traceback: lock.__exit__(exc_type, exc_value, traceback)

    def use_fcntl(self):
        fp = open(self.path, 'w')
        self.enter = lambda: fcntl.flock(fp, fcntl.LOCK_EX)
        self.exit = lambda exc_type, exc_value, traceback: fp.close()

    def __enter__(self):
        self.enter()

    def __exit__(self, exc_type, exc_value, traceback):
        self.exit(exc_type, exc_value, traceback)


class GpgLock(FileLock):
    """Minor subclass that locks the GPG private key."""

    def __init__(self, **kwargs):
        kwargs['path'] = os.path.join(settings.GPG.gnupghome, 'secring.gpg')
        super(GpgLock, self).__init__(**kwargs)
