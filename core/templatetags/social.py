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

from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()
_purpose = {
    'share-account': {
        'data_title': _('Just registered my new #Jabber account "%(username)s" on %(domain)s. Register too and add me! #xmpp'),
    },
    'default': {
        'data_title': _('Register your new #Jabber account on %(homepage)s via %(register_url)s. #xmpp'),
    },
}


@register.inclusion_tag("core/social.html", takes_context=True)
def social(context, noauto=False, purpose='default'):
    """
    Parameters
    ----------

    noauto : bool, optional
        If True, display fake shariff buttons to directly follow the site on Facebook/Twitter.
        The label is obviously somewhat of a misnomer.
    """
    passed_context = {
        'ENABLE_SOCIAL_BUTTONS': context.get('ENABLE_SOCIAL_BUTTONS', True),
        'SITE': context['SITE'],
        'noauto': noauto,
        'register_url': context['REGISTER_URL'],
    }

    i18n_context = {
        'username': context.get('username'),
        'homepage': context['SITE']['HOMEPAGE'],
        'action_url': context.get('ACTION_URL'),
        'domain': context['SITE']['DOMAIN'],
        'register_url': context['REGISTER_URL'],
    }
    for key, value in _purpose[purpose].items():
        passed_context[key] = value % i18n_context

    if context['SITE'].get('FACEBOOK'):
        passed_context['FACEBOOK_URL'] = 'https://www.facebook.com/%s' % context['SITE']['FACEBOOK']
    return passed_context
