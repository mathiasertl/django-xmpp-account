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

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.forms import UserCreationFormNoPassword
from core.models import Confirmation
from core.models import Address
from core.models import UserAddresses
from core.models import RegistrationUser
from register.views import RegistrationView
from reset.views import ResetPasswordView
from reset.views import ResetEmailView

User = get_user_model()


class UserAddressAdmin(admin.ModelAdmin):
    list_display = ['purpose', 'address', 'user', 'timestamp', ]
    list_select_related = ('address', 'user', )
    search_fields = ('address__address', 'user__email', 'user__username')


class AddressAdmin(admin.ModelAdmin):
    list_display = ['address', 'count_activities', 'timerange']

    def queryset(self, request):
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


class RegistrationUserAdmin(admin.ModelAdmin):
    list_display = ['jid', 'email', 'registered', 'confirmed']
    ordering = ('-registered', '-confirmed', )
    search_fields = ('username', 'email', )
    list_filter = (RegistrationMethodListFilter, )
    actions = (
        'resend_registration',
        'resend_password_reset',
        'resend_email_reset',
    )

    def resend_registration(self, request, queryset):
        for user in queryset:
            key = Confirmation.objects.create(user=user, purpose=RegistrationView.purpose)
            key.send(
                request=request, template_base=RegistrationView.email_template,
                subject=RegistrationView.email_subject % {'domain': user.domain, },
                confirm_url_name=RegistrationView.confirm_url_name
            )
    resend_registration.short_description = _("Resend registration email")

    def resend_password_reset(self, request, queryset):
        for user in queryset:
            key = Confirmation.objects.create(user=user, purpose=ResetPasswordView.purpose)
            key.send(
                request=request, template_base=ResetPasswordView.email_template,
                subject=ResetPasswordView.email_subject % {'domain': user.domain, },
                confirm_url_name=ResetPasswordView.confirm_url_name
            )
    resend_password_reset.short_description = _("Resend password reset email")

    def resend_email_reset(self, request, queryset):
        for user in queryset:
            key = Confirmation.objects.create(user=user, purpose=ResetEmailView.purpose)
            key.send(
                request=request, template_base=ResetEmailView.email_template,
                subject=ResetEmailView.email_subject % {'domain': user.domain, },
                confirm_url_name=ResetEmailView.confirm_url_name
            )
    resend_email_reset.short_description = _("Resend email reset email")

    def jid(self, obj):
        return '%s@%s' % (obj.username, obj.domain)


class UserAdmin(UserAdminBase):
    add_form = UserCreationFormNoPassword


admin.site.register(Confirmation)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserAddresses, UserAddressAdmin)
admin.site.register(RegistrationUser, RegistrationUserAdmin)
admin.site.unregister(Group)

# Replace core user admin UserAdmin:
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
