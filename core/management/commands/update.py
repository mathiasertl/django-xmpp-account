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

import os

from datetime import datetime
from datetime import timedelta
from subprocess import PIPE
from subprocess import Popen

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        os.chdir(settings.PROJECT_ROOT)

        call_command('syncdb', noinput=True, migrate=True)
        if settings.STATIC_ROOT:
            call_command('collectstatic', interactive=False)

        for app in ['core', 'register', 'reset', 'delete']:
            curdir = os.path.abspath(os.getcwd())

            try:
                os.chdir(app)
                call_command('compilemessages')
            finally:
                os.chdir(curdir)
