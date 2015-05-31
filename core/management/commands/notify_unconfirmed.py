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

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.template import Context
from django.template import loader

from backends import backend

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        users = User.objects.filter(email__isnull=True)

        template = loader.get_template('reset/notify_inconfirmed.txt')
        subject = "Please set your email address at https://account.jabber.at"

        for user in users:
            context = Context({
                'user': user.username,
                'domain': user.domain,
            })
            message = template.render(context)
            backend.message(user.username, user.domain, subject, message)
