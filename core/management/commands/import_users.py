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

import codecs
import logging
import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from django_xmpp_backends import backend
from core.constants import REGISTRATION_INBAND

User = get_user_model()
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
log = logging.getLogger('cleanup')  # we log to a file


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--dry', default=False, action='store_true',
                            help="Do not actually import users.")
        parser.add_argument('domain')

    def handle(self, *args, **kwargs):
        domain = kwargs['domain']
        if domain not in settings.XMPP_HOSTS:
            raise CommandError("%s: Domain not configured in XMPP_HOSTS setting." % domain)

        backend_users = set([u.lower() for u in backend.all_users(domain)])
        db_users = User.objects.filter(jid__endswith='@%s' % domain).values_list('jid', flat=True)
        db_users = set([u.split('@', 1)[0] for u in db_users])
        to_create = backend_users - db_users

        if not kwargs.get('dry'):
            for username in to_create:
                jid = '%s@%s' % (username, domain)
                User.objects.create(jid=jid, registration_method=REGISTRATION_INBAND)

        self.stdout.write("Imported %s users." % len(to_create))
