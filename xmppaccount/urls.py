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

from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url

from register.views import RegistrationView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^$', RegistrationView.as_view(), name='index'),

    # for captchas:
    url(r'^captcha/', include('captcha.urls')),

    # core URLs
    url(r'^core/', include('core.urls')),
    url(r'^register/', include('register.urls')),
    url(r'^reset/', include('reset.urls')),
    url(r'^delete/', include('delete.urls')),

    # admin interface
    url(r'^admin/', include(admin.site.urls)),
]

for path, include_args in settings.EXTRA_URL_INCLUDES.items():
    urlpatterns.append(url(path, include(*include_args)))
