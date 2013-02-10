from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin, staticfiles
from ePolonica.settings import LOGIN_URL, LOGOUT_URL
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ePolonica.views.home', name='home'),
    # url(r'^ePolonica/', include('ePolonica.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^', include('core.urls') ),
   # (r'^', include('places.urls') ),
    (r'^places/', include('places.urls') ),
    (r'^search/', include('search.urls') ),
    (r'^media/(?P<path>.*)$', 'core.views.MediaView'),
    ( LOGIN_URL , 'django.contrib.auth.views.login'),
    ( LOGOUT_URL , 'django.contrib.auth.views.logout' ),
)
