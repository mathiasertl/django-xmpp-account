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

import logging

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render
from django.utils import six

from core.exceptions import RateException
from core.exceptions import RegistrationRateException
from core.exceptions import SpamException
from core.exceptions import TemporaryError

log = logging.getLogger(__name__)


class SiteMiddleware(object):
    def process_request(self, request):
        host = request.META.get('HTTP_HOST', request.META.get('SERVER_NAME'))
        mapped = settings.XMPP_HOSTS_MAPPING.get(host)
        if mapped is None:
            request.site = settings.XMPP_HOSTS[settings.DEFAULT_XMPP_HOST]
            request.site['DOMAIN'] = settings.DEFAULT_XMPP_HOST
            request.site.setdefault('BRAND', settings.BRAND or settings.DEFAULT_XMPP_HOST)
        else:
            request.site = settings.XMPP_HOSTS[mapped]
            request.site['DOMAIN'] = mapped
            request.site.setdefault('BRAND', settings.BRAND or mapped)

        request.site.setdefault('CONTACT_URL', settings.CONTACT_URL)
        request.site.setdefault('FROM_EMAIL', settings.DEFAULT_FROM_EMAIL)


class AntiSpamMiddleware(object):
    def process_request(self, request):
        host = request.META['REMOTE_ADDR']

        message = cache.get('spamblock-%s' % host)  # Added by previous SpamException
        if message:
            context = {
                'EXCEPTION': message,
                'HOST': host,
            }
            return render(request, 'core/spambot.html', context)

    def process_exception(self, request, exception):
        host = request.META['REMOTE_ADDR']

        if six.PY3:
            message = ' '.join(exception.args)
        else:
            #TODO: This still is sometimes True!
            message = exception.message or 'UNKNOWN REASON'

        context = {
            'EXCEPTION': message,
            'HOST': host,
        }

        if isinstance(exception, SpamException):
            cache.set('spamblock-%s' % host, context['EXCEPTION'], settings.SPAM_BLOCK_TIME)
            return render(request, 'core/spambot.html', context)
        elif isinstance(exception, RegistrationRateException):
            return render(request, 'core/registration_rate.html', context)
        elif isinstance(exception, RateException):
            log.info('RateException: %s', message)
            return render(request, 'core/rate.html', context)
        elif isinstance(exception, TemporaryError):
            return render(request, 'core/temporary_error.html', context)
