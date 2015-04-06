# -*- coding: utf-8 -*-
#
# This file is part of django-xmpp-account (https://github.com/mathiasertl/django-xmpp-account/).
#
# django-xmpp-account is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# django-xmpp-account is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# django-xmpp-account.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

from django import template
from django.utils.translation import ugettext as _
from django.templatetags.static import static

register = template.Library()


@register.simple_tag(takes_context=True)
def follow(context):
    """A Twitter follow button."""
    account = context['SITE'].get('TWITTER')
    if account is None:
        return ''

    target = 'https://twitter.com/intent/follow?screen_name=%s&tw_p=followbutton' % account
    image_src = static('site/follow_%s.png' % account)
    image = '<img class="social-button" src="%s" alt="%s" data-url="%s" data-width="570" ' \
        'data-height="450">' % (image_src, _("Follow @%s on Twitter") % account, target)
    return image


@register.simple_tag(takes_context=True)
def share(context):
    """A Facebook share button."""
    account = context['SITE'].get('FACEBOOK')
    if account is None:
        return ''

    action = context['ACTION_URL']
    target = 'https://www.facebook.com/sharer/sharer.php?u=%s' % action
    image_src = static('site/share.png')
    return '<img class="social-button" src="%s" alt="%s" data-url="%s" data-width="670" ' \
        'data-height="450">' % (image_src, _("Share this page on Facebook"), target)

@register.simple_tag(takes_context=True)
def fb_follow(context):
    """A button to follow a page on facebook."""
    account = context['SITE'].get('FACEBOOK')
    if account is None:
        return ''

    action = context['ACTION_URL']
