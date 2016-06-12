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

from __future__ import unicode_literals, absolute_import

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from django_confirm.models import Confirmation

from .constants import PURPOSE_REGISTER
from .constants import PURPOSE_SET_EMAIL
from .constants import PURPOSE_SET_PASSWORD
from .constants import PURPOSE_DELETE

PURPOSES = {
    PURPOSE_REGISTER: {
        'subject': _('Your new account on %(domain)s'),
    },
    PURPOSE_SET_EMAIL: {
        'subject': _('Confirm the email address for your %(domain)s account'),
    },
    PURPOSE_SET_PASSWORD: {
        'subject': _('Reset the password for your %(domain)s account'),
    },
    PURPOSE_DELETE: {
        'subject': _('Delete your account on %(domain)s'),
    },
}


class XMPPAccountConfirmation(Confirmation):
    class Meta:
        proxy = True

    def send(self, purpose, request, user, **kwargs):
        node, domain = user.get_username().split('@', 1)
        subject = PURPOSES[self.purpose]['subject'] % {
            'domain': domain,
        }
        path = reverse('xmpp_accounts:%s_confirm' % purpose, kwargs={'key': self.key, })
        uri = request.build_absolute_uri(location=path)

        kwargs.setdefault('subject', subject)
        kwargs.setdefault('sender', request.site.get('FROM_EMAIL', settings.DEFAULT_FROM_EMAIL))
        kwargs.setdefault('txt_template', 'xmpp_accounts/%s/mail.txt' % purpose)
        kwargs.setdefault('html_template', 'xmpp_accounts/%s/mail.html' % purpose)
        kwargs.setdefault('lang', request.LANGUAGE_CODE)
        kwargs.setdefault('gpg_opts', getattr(settings, 'GNUPG', None))

        kwargs.setdefault('extra_context', {})
        kwargs['extra_context'].update({
            'username': node,
            'domain': domain,
            'jid': user.get_username(),
            'cleartext': settings.CLEARTEXT_PASSWORDS,
            'uri': uri,
        })
        return super(XMPPAccountConfirmation, self).send(**kwargs)
