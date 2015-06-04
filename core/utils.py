# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:hlsearch
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

from __future__ import unicode_literals

import random
import string
import threading

from django.conf import settings
from django.core.urlresolvers import reverse

SAFE_CHARS = string.ascii_letters + string.digits


def random_string(length=32):
    return ''.join(random.choice(SAFE_CHARS) for x in range(length))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def confirm(request, user, purpose, payload=None, lang=None):
    """Send an email confirmation from a request - either via Celery or directly."""

    if lang is None:
        lang = settings.LANGUAGE_CODE
    if payload is None:
        payload = {}

    urlname, key = user.get_confirmation_key(purpose, payload)

    path = reverse(urlname, kwargs={'key': key, })
    uri = request.build_absolute_uri(location=path)

    key.send(uri=uri, site=request.site, lang=lang)

gpg_lock = threading.Lock()
