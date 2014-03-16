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

import sys

import sleekxmpp

from django.conf import settings
from django.core.management.base import BaseCommand

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input


class EjabberdClient(sleekxmpp.ClientXMPP):
    """
    Example messages::

        [2014-03-16 16:52:29] username@jabber.at was registered from IP address ::FFFF:1.2.3.4 on node ejabberd@host using mod_register.
        [2014-03-16 16:52:29] username@jabber.at was registered from IP address 2001::1 on node ejabberd@host using mod_register.
    """

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("message", self.message)

    def start(self, event):
        print('start')
        self.send_presence()
        self.get_roster()

    def message(self, msg):
        print(msg)
        if msg['type'] in ('chat', 'normal'):
            msg.reply("Thanks for sending\n%(body)s" % msg).send()



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        bot = EjabberdClient(settings.EJABBERD_REGISTRATION_BOT['jid'],
                             settings.EJABBERD_REGISTRATION_BOT['password'])

        if bot.connect():
            bot.process(block=False)
        else:
            print('unable to connect')
