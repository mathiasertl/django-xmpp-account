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
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import ugettext_lazy as _

from backends import backend
from core.constants import PURPOSE_REGISTER
from core.constants import PURPOSE_SET_EMAIL
from core.constants import PURPOSE_SET_PASSWORD
from core.forms import UserCreationFormNoPassword
from core.models import Confirmation
from core.models import Address
from core.models import UserAddresses
from core.models import RegistrationUser
from core.tasks import send_email
from core.utils import confirm

User = get_user_model()


class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['purpose', 'address', 'user', 'timestamp', ]
    list_select_related = ('address', 'user', )
    search_fields = ('address__address', 'user__email', 'user__username')


class AddressAdmin(admin.ModelAdmin):
    list_display = ['address', 'count_activities', 'timerange']

    def get_queryset(self, request):
        qs = super(AddressAdmin, self).queryset(request)
        return qs.annotate(
            count_activities=models.Count('activities')
        ).annotate(
            first_activity=models.Min('useraddresses__timestamp')
        ).annotate(
            last_activity=models.Max('useraddresses__timestamp')
        )

    def timerange(self, obj):
        if obj.count_activities <= 1:
            return '-'
        diff = obj.last_activity - obj.first_activity
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        obj.timerange = diff

        return '%s days, %s:%s:%s' % (diff.days, hours, minutes, seconds)
    timerange.short_description = 'Timerange of activities'

    def count_activities(self, obj):
        return obj.count_activities
    count_activities.short_description = 'Number of activities'
    count_activities.admin_order_field = 'count_activities'


class RegistrationMethodListFilter(admin.SimpleListFilter):
    title = _('Registration method')
    parameter_name = 'method'

    def lookups(self, request, model_admin):
        return (
            ('ibr', _('In-Band registration')),
            ('site', _('This website')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'ibr':
            return queryset.filter(email__isnull=True)
        elif self.value() == 'site':
            return queryset.filter(email__isnull=False)
        return queryset


class DomainFilter(admin.SimpleListFilter):
    title = _('domain')
    parameter_name = 'domain'

    def lookups(self, request, model_admin):
        return {k: k for k in settings.XMPP_HOSTS}.items()

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(jid__endswith='@%s' % self.value())
        return queryset


class RegistrationUserAdmin(admin.ModelAdmin):
    list_display = ['jid', 'email', 'registered', 'confirmed']
    ordering = ('-registered', '-confirmed', )
    search_fields = ('jid', 'email', )
    list_filter = (DomainFilter, 'registration_method', )
    actions = (
        'resend_registration',
        'resend_password_reset',
        'resend_email_reset',
    )
    fields = (
        'jid', 'email', 'registered', 'registration_method', 'confirmed', 'gpg_fingerprint',
        'is_admin',
    )
    readonly_fields = ('registered', 'confirmed', )

    def log_deletion(self, request, object, object_repr):
        """Remove users from Jabber server before removing from database.

        This is unfortunately the only good method to hook into.
        """
        username = object.username
        domain = object.domain
        super(RegistrationUserAdmin, self).log_deletion(request, object, object_repr)
        backend.remove(username, domain)

    def _confirm(self, request, user, purpose, payload=None):
        key, kwargs = confirm(request, user, purpose=purpose, payload=payload)
        if settings.BROKER_URL is None:
            key.send(**kwargs)
        else:
            send_email.delay(key_id=key.pk, **kwargs)

    def save_model(self, request, obj, form, change):
        site = settings.XMPP_HOSTS[obj.domain]

        obj.save()
        if change is True:  # changed user
            from_db = User.objects.only('email').get(jid=obj.jid)
            if from_db.email != form.cleaned_data['email']:
                payload = {
                    'gpg_fingerprint': form.cleaned_data.get('gpg_fingerprint'),
                    'email': form.cleaned_data['email'],
                }
                self._confirm(request, obj, purpose=PURPOSE_REGISTER, payload=payload)
        else: # new user
            if site.get('RESERVE', False):
                backend.reserve(username=obj.username, domain=obj.domain, email=obj.email)
            if obj.email:
                self._confirm(request, obj, purpose=PURPOSE_REGISTER)

    def resend_registration(self, request, queryset):
        for user in queryset:
            #TODO: This does not use the original payload - e.g. GPG encryption
            self._confirm(request, user, purpose=PURPOSE_REGISTER)
    resend_registration.short_description = _("Resend registration email")

    def resend_password_reset(self, request, queryset):
        for user in queryset:
            self._confirm(request, user, purpose=PURPOSE_SET_PASSWORD)
    resend_password_reset.short_description = _("Resend password reset email")

    def resend_email_reset(self, request, queryset):
        for user in queryset:
            #TODO: This does not use the original payload - e.g. GPG encryption
            self._confirm(request, user, purpose=PURPOSE_SET_EMAIL)
    resend_email_reset.short_description = _("Resend email reset email")



class UserAdmin(UserAdminBase):
    add_form = UserCreationFormNoPassword


admin.site.register(Confirmation)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserAddresses, UserAddressAdmin)
admin.site.register(RegistrationUser, RegistrationUserAdmin)
admin.site.unregister(Group)

# Replace core user admin UserAdmin:
#admin.site.unregister(User)
#admin.site.register(User, UserAdmin)
