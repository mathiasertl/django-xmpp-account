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

from __future__ import unicode_literals, absolute_import

from django.conf.urls import url

from . import views

app_name = 'xmpp_accounts'

urlpatterns = [
    url(r'^$', views.NewRegistrationView.as_view(), name='register'),

    url(r'^register/confirm/(?P<key>\w+)/$', views.RegistrationConfirmationView.as_view(),
        name='register_confirm'),
    url(r'^password/$', views.ResetPasswordView.as_view(), name='reset_password'),
    url(r'^password/confirm/(?P<key>\w+)/$', views.ResetPasswordConfirmationView.as_view(),
        name='reset_password_confirm'),
    url(r'^email/$', views.ResetEmailView.as_view(), name='reset_email'),
    url(r'^email/confirm/(?P<key>\w+)/$', views.ResetEmailConfirmationView.as_view(),
        name='reset_email_confirm'),
    url(r'^delete/$', views.DeleteView.as_view(), name='delete'),
    url(r'^delete/confirm/(?P<key>\w+)/$', views.DeleteConfirmationView.as_view(),
        name='delete_confirm'),
    url(r'^api/user-available/$', views.UserAvailableView.as_view(), name='api-user-available'),

]
