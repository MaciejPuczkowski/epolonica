from django.conf.urls import patterns, include, url
import views
from core.views import AuthoredFormView, ProfileView, UserFormView,\
    PublicProfileView, ObservedUsersView, ObservedContentsView, HistoryView,\
    EventsView, VoteContentView, RegistrationView, ActivationView,\
    ReactivationView, Redirection, MessageView, ObserveUser, ObserveContent,\
    ObservingUsersView, MessageCreateView, MessageListView, RespondView,\
    CommentsView, ReportUserView, ReportContentView
from core.forms import MessageForm, ReportContentForm, ReportUserForm,\
    ReportErrorForm, AddressForm
from core.models import Message, ReportContent, ReportUser, ReportError, Photo,\
    Address
from django.views.generic.list import ListView
from places.forms import PhotoForm
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView
urlpatterns = patterns('core',
    (r'^mailbox/list.html$', MessageListView.as_view( )  ),
    (r'^mailbox/send.html$', MessageCreateView.as_view()  ),
    (r'^mailbox/respond,(?P<id>\d+).html$', RespondView.as_view()  ),
    (r'^mailbox/message,(?P<id>\d+).html$', MessageView.as_view( template_name = "core/message.html" )  ),
    (r'^report/content,(?P<id>\d+).html$', ReportContentView.as_view( form_class = ReportContentForm, model = ReportContent, success_url = "/report/success.html" ) ),
    (r'^report/user,(?P<id>\d+).html$', ReportUserView.as_view( form_class = ReportUserForm, model = ReportUser, success_url = "/report/success.html" ) ),
    (r'^report/error.html$', AuthoredFormView.as_view( form_class = ReportErrorForm, model = ReportError, success_url = "/report/success.html" ) ),
    (r'^report/success.html$', TemplateView.as_view( template_name = "core/report_success.html" ) ),
    (r'^profile.html$', ProfileView.as_view() ),
    (r'^profile/edit/image$', UserFormView.as_view( form_class = PhotoForm, model = Photo, success_url = "/profile.html" ) ),
    (r'^profile/edit/address$', UserFormView.as_view( form_class = AddressForm, model = Address , success_url = "/profile.html" ) ),
    (r'^user,(?P<id>\d+).html$', PublicProfileView.as_view() ),
    (r'^obervers.html$', ListView.as_view( model = User, template_name = "core/users.html" ) ),
    (r'^observed/users.html$', ObservedUsersView.as_view() ),
    (r'^observing/users.html$', ObservingUsersView.as_view() ),
    (r'^observe/user,(?P<id>\d+)/$', ObserveUser.as_view() ),
    (r'^observe/content,(?P<id>\d+)/$', ObserveContent.as_view() ),
    (r'^history.html$', HistoryView.as_view() ),
    (r'^events.html$', EventsView.as_view() ),
    (r'^(?P<time>[0-9.]+),events.html$', EventsView.as_view( template_name = "core/cyclic_events.html" ) ),
    (r'^vote/(?P<id>\d+)$', VoteContentView.as_view() ),
    (r'^register.html$', RegistrationView.as_view() ),
    (r'^activate/(?P<id>\d+)/(?P<code>.*)/$', ActivationView.as_view() ),
    (r'^reactivate,(?P<id>\d+).html$', ReactivationView.as_view()),
    (r'^$', Redirection.as_view( to = "/places/")),
    (r'^accounts/profile/$', Redirection.as_view( to = "/places/")),
    (r'^comment/(?P<id>\d+)$', CommentsView.as_view() )
    
    
    
)