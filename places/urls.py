from django.conf.urls import patterns, include, url
import views
from places.views import PlaceListView, PlaceView, PhotoListView, ArticleView,\
    PhotoView, ArticleListView, CreatePlaceView, EditPlaceView,\
    CreatePlaceContentView, PublishedView, EditArticleView, EditPhotoView,\
    UrlPlaceListView
from places.models import Place, Photo, Article, PlaceTranslation
from places.forms import PlaceForm, ArticleForm, PhotoForm, TranslatePlaceForm
from core.views import ObservedContentsView, TranslateView
urlpatterns = patterns('',
    (r'^$', PlaceListView.as_view() ),
    (r'^page_(?P<page>\d)$', PlaceListView.as_view() ),
    (r'^place,(?P<title>[^,]*),(?P<id>\d+).html$', PlaceView.as_view() ),
    (r'^published.html$', UrlPlaceListView.as_view( ) ),
    (r'^promoted.html$', UrlPlaceListView.as_view( title = "Promoted", template_name = "plist.html" ) ),
    (r'^(?P<title>[^,]*),(?P<lang>[^,]*),(?P<id>\d+).html$', PlaceView.as_view() ),
    (r'^(?P<title>.*),(?P<id>\d)/gallery,(?P<page>\d).html$', PhotoListView.as_view() ),
    (r'^(?P<title>.*),(?P<id>\d)/articles,(?P<page>\d).html$', ArticleListView.as_view() ),
    (r'^article/(?P<title>.*),(?P<id>\d).html$', ArticleView.as_view() ),
    (r'^(?P<title>.*),(?P<id>\d)/gallery,(?P<page>\d)$', PhotoListView.as_view() ),
    (r'^photo/(?P<title>.*),(?P<id>\d).html$', PhotoView.as_view() ),
    (r'^add.html$', CreatePlaceView.as_view() ),
    (r'^translate/(?P<id>\d*).html$', TranslateView.as_view( form_class = TranslatePlaceForm, model = Place, trans_model = PlaceTranslation ) ),
    (r'^(?P<id>\d)/add_photo.html$', CreatePlaceContentView.as_view( form_class = PhotoForm ) ),
    (r'^(?P<id>\d+)/add_article.html$', CreatePlaceContentView.as_view( form_class = ArticleForm ) ),
    (r'^edit,(?P<id>\d+).html$', EditPlaceView.as_view() ),
    (r'^edit/photo,(?P<id>\d+).html$', EditPhotoView.as_view( )),
    (r'^edit/article,(?P<id>\d+).html$', EditArticleView.as_view( )),
    (r'^observed.html$', ObservedContentsView.as_view( template_name = "places/places.html", model = Place ) ),
    
)