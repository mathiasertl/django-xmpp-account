from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from register.views import RegistrationView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', RegistrationView.as_view(), name='index'),

    url(r'^register/', include('register.urls')),
    url(r'^reset/', include('reset.urls')),
    url(r'^delete/', include('delete.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
