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

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render

from core.exceptions import RateException
from core.exceptions import RegistrationRateException
from core.exceptions import SpamException
from core.exceptions import TemporaryError


class SiteMiddleware(object):
    def process_request(self, request):
        mapped = settings.XMPP_HOSTS_MAPPING.get(request.META['HTTP_HOST'])
        if mapped is None:
            request.site = settings.XMPP_HOSTS[settings.DEFAULT_XMPP_HOST]
            request.site.setdefault('BRAND', settings.BRAND or settings.DEFAULT_XMPP_HOST)
        else:
            request.site = settings.XMPP_HOSTS[mapped]
            request.site.setdefault('BRAND', settings.BRAND or mapped)


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

        context = {
            'EXCEPTION': exception.message or 'UNKNOWN REASON',
            'HOST': host,
        }

        if isinstance(exception, SpamException):
            cache.set('spamblock-%s' % host, context['EXCEPTION'], settings.SPAM_BLOCK_TIME)
            return render(request, 'core/spambot.html', context)
        elif isinstance(exception, RegistrationRateException):
            return render(request, 'core/registration_rate.html', context)
        elif isinstance(exception, RateException):
            return render(request, 'core/rate.html', context)
        elif isinstance(exception, TemporaryError):
            return render(request, 'core/temporary_error.html', context)
