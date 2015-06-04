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

from __future__ import absolute_import

import logging
import time

from celery import shared_task

from core.lock import FileLock
from core.models import Confirmation

log = logging.getLogger(__name__)


@shared_task(bind=True)
def send_email(self, key_id, uri, site, lang):
    key = Confirmation.objects.get(id=key_id)
    key.send(uri=uri, site=site, lang=lang)


@shared_task(bind=True)
def test_task(self):
    with FileLock('testpath', getattr(self.backend, 'client')):
        log.warn('locked')
        time.sleep(60)
    log.warn('after lock')
