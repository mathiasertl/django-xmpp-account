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

import json
import logging
import os
import time

from celery import shared_task

from django.conf import settings

from core.lock import FileLock
from core.models import Confirmation

log = logging.getLogger(__name__)


@shared_task(bind=True)
def send_email(self, key_id, uri, site, lang):
    key = Confirmation.objects.get(id=key_id)

    payload = json.loads(key.payload)
    frm, recipient, subject, text, html = key.get_msg_data(payload, uri, site, lang)

    if key.should_use_gpg(payload=payload, site=site):
        send_gpg_email.delay(key_id=key_id, site=site, frm=frm, subject=subject, text=text, html=html)
    else:
        msg = key.msg_without_gpg(subject, frm, recipient, text, html)
        msg.send()


@shared_task(bind=True)
def send_gpg_email(self, key_id, site, frm, subject, text, html):
    lock_path = os.path.join(settings.GPG.gnupghome, 'secring.gpg')

    key = Confirmation.objects.get(id=key_id)

    with FileLock(lock_path, getattr(self.backend, 'client')):
        msg = key.msg_with_gpg(site, frm, subject, text, html)

    msg.send()


@shared_task(bind=True)
def test_task(self):
    with FileLock('testpath', getattr(self.backend, 'client')):
        log.warn('locked')
        time.sleep(60)
    log.warn('after lock')
