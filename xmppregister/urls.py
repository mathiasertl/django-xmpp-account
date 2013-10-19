from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from register.views import IndexView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', IndexView.as_view(), name='index'),
    # Examples:
    # url(r'^$', 'xmppregister.views.home', name='home'),
    # url(r'^xmppregister/', include('xmppregister.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
