from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin, staticfiles
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ePolonica.views.home', name='home'),
    # url(r'^ePolonica/', include('ePolonica.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    (r'^system/', include('core.urls') ),
   # (r'^', include('places.urls') ),
    (r'^registration/', include('registration.urls') ),
    (r'^media/(?P<path>.*)$', 'core.views.MediaView'),
)
