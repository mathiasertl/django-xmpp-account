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

import logging
import re
import sys
import time

from datetime import datetime
from optparse import make_option

import pytz
import sleekxmpp

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.constants import PURPOSE_REGISTER
from core.constants import REGISTRATION_INBAND
from core.models import Address
from core.models import UserAddresses

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input

User = get_user_model()
REGEX = '\[([^\]]*)\]\s*The account ([^@]*)@([^\s]*) was registered from IP address ([^\s]*)'

tzinfo = pytz.timezone(settings.TIME_ZONE)
log = logging.getLogger('import')


class EjabberdClient(sleekxmpp.ClientXMPP):
    """
    Example messages::

        [2014-03-16 16:52:29] The account username@host was registered from IP address ::FFFF:1.2.3.4 on node ejabberd@host using mod_register.
        [2014-03-16 16:52:29] The account username@host was registered from IP address 2001::1 on node ejabberd@host using mod_register.
    """

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    def start(self, event):
        self.send_presence()

    def message(self, msg):
        try:
            timestamp, username, domain, ip = re.match(REGEX, msg['body']).groups()
            if ip.lower().startswith('::ffff:'):
                ip = ip[7:]

            if domain != msg['from'].full:
                log.warn('Received message from unauthorized JID %s', msg['from'].full)
                return

            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            timestamp = tzinfo.localize(timestamp, is_dst=None)
            address = Address.objects.get_or_create(address=ip)[0]

            try:
                user = User.objects.get(username=username, domain=domain)
                # a user that already exists is a state that should not happen, hence log an error
                log.error('User exists: %s@%s', username, domain)
                return
            except User.DoesNotExist:
                user = User.objects.create(username=username, domain=domain,
                                           registration_method=REGISTRATION_INBAND,
                                           registered=timestamp)

            log.info('Imported user %s@%s (from %s)', username, domain, ip)
            UserAddresses.objects.create(address=address, user=user, purpose=PURPOSE_REGISTER)
        except Exception as e:
            log.error('%s: %s', type(e).__name__, e)
            return


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-q', '--quiet', action='store_true', default=False,
                    help="Do not output deleted users."),
    )

    def handle(self, *args, **kwargs):
        if kwargs.get('quiet'):
            log.setLevel('WARN')

        bot = EjabberdClient(settings.EJABBERD_REGISTRATION_BOT['jid'],
                             settings.EJABBERD_REGISTRATION_BOT['password'])

        if bot.connect():
            bot.process(block=False)
            time.sleep(5)
            bot.disconnect(wait=True)
        else:
            log.error('Unable to connect.')
