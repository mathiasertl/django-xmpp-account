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

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class BootstrapMixin(object):
    """Mixin that adds the form-control class used by bootstrap to input widgets."""

    def __init__(self, **kwargs):
        super(BootstrapMixin, self).__init__(**kwargs)
        if self.widget.attrs.get('class'):
            self.widget.attrs['class'] += ' form-control'
        else:
            self.widget.attrs['class'] = 'form-control'


class XMPPAccountEmailField(BootstrapMixin, forms.EmailField):
    def __init__(self, **kwargs):
        kwargs.setdefault('label', _('email'))
        kwargs.setdefault(
            'help_text', _('Required, a confirmation email will be sent to this address.'))
        kwargs.setdefault('error_messages', {})
        kwargs['error_messages'].setdefault(
            'own-domain',
            _("This Jabber host does not provide email addresses. You're supposed to give your own "
              "email address."))
        kwargs['error_messages'].setdefault(
            'blocked-domain',
            _("Email addresses with this domain are blocked and cannot be used on this site."))

        super(XMPPAccountEmailField, self).__init__(**kwargs)

    def clean(self, value):
        email = super(XMPPAccountEmailField, self).clean(value)
        hostname = email.rsplit('@', 1)[1]

        if hostname in getattr(settings, 'NO_EMAIL_HOSTS', []):
            raise forms.ValidationError(self.error_messages['own-domain'])
        if hostname in getattr(settings, 'BLOCKED_EMAIL_TLDS', []):
                raise forms.ValidationError(self.error_messages['blocked-domain'])
        return email
