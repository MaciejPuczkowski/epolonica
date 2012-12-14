from django.conf.urls import patterns, include, url
import views
urlpatterns = patterns('registration',
    (r'^form.html$', views.RegistrationView.as_view() ),    
)