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

import logging
import fcntl

from django.core.cache import caches

from redis.client import Redis

log = logging.getLogger(__name__)
cache = caches['default']


class FileLock(object):
    def __init__(self, path, cache_fallback=None):
        self.path = '%s.xmppaccount.lock' % path
        self.cache = cache_fallback

        # (1) Try to use standard django cache
        #     # memcached: https://russellneufeld.wordpress.com/2012/05/24/using-memcached-as-a-distributed-lock-from-within-django/
        #     # redis: http://loose-bits.com/2010/10/distributed-task-locking-in-celery.html
        if cache.__module__ == 'django_redis.cache':
            # TODO: solve this without a module-level import
            log.warn('use django redis cache')
            self.use_redis(cache.client.get_client(True))

        # Try to use passed cache as fallback. This is only used when no suitable main cache is
        # found, because the main cache is shared between the WSGI server and Celery.
        elif isinstance(cache_fallback, Redis):
            log.warn('Use Redis from Celery')
            self.use_redis(cache_fallback)

        # Try to use fcntl
        elif True:  # TODO: Test here if we porperly support fcntl
            log.warn('Use fcntl')
            self.use_fcntl()
        else:
            log.warn('No suitable locking mechanism found')

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
