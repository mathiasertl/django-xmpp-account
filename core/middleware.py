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
from django.core.cache import cache
from django.shortcuts import render

from core.exceptions import SpamException


class AntiSpamMiddleware(object):
    def process_request(self, request):
        host = request.get_host()
        if cache.get('spamblock-%s' % host):
            return render(request, 'core/spambot.html')

    def process_exception(self, request, exception):
        host = request.get_host()

        if isinstance(exception, SpamException):
            cache.set('spamblock-%s' % host, True, settings.SPAM_BLOCK_TIME)
            return render(request, 'core/spambot.html')
