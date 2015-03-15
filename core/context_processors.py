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


def xmppaccount(request):
    submit = settings.DEBUG and request.GET.get('submit')
    context = {
        'MIN_USERNAME_LENGTH': settings.MIN_USERNAME_LENGTH,
        'MAX_USERNAME_LENGTH': settings.MAX_USERNAME_LENGTH,
        'SITE': request.site,  # added by middleware, mappes to a host in XMPP_HOSTS
        'SUBMIT': submit,
        'USE_GPG': settings.GPG is not None,
    }
    if submit:
        context.update({k: v for k, v in request.GET.items()})
    return context
