from django.conf.urls import patterns, include, url
from search.views import SearchContents

urlpatterns = patterns('',
    (r'^contents.html$', SearchContents.as_view( template_name = "places/places.html") ),
    
)