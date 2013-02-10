# -*- coding: utf-8 -*-
from django.views.generic import ListView, View
from places.models import Place, Article, Photo, PlaceTranslation
from django.views.generic.edit import FormView
from places.forms import PlaceForm, ArticleForm, PlaceEditForm, ArticleEditForm,\
    PhotoEditForm
from django.shortcuts import render_to_response
from django.utils.decorators import classonlymethod
from django.core.context_processors import csrf
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404
from ePolonica.settings import MEDIA_URL, CONTENT_LANGUAGE_CODE
from core.models import Vote, UserEvent, UserMetaData, Translation, TLanguage
from core.forms import CommentForm
PAGE_ARTICLES = 5
PAGE_PHOTOS = 10

class PlaceView( View ):
    template_name = "places/place.html"
    def dispatch(self, request, *args, **kwargs):
        try:
            _id = kwargs["id"]
          
            data = { "MEDIA_URL" : MEDIA_URL }
            data[ "place" ] =  Place.objects.get( id = _id ) 
            data["place"].visited += 1; 
            data["place"].save()
            data["place"].comment_form = CommentForm( initial= { "content" : data["place"]} )
            if request.user.is_authenticated():
                meta = UserMetaData.objects.get( user = request.user )
                if meta.language is not None and meta.language.short != CONTENT_LANGUAGE_CODE and not "lang" in kwargs:
                    kwargs["lang"] = meta.language
            translations = data["place"].translations.all()
            if "lang" in kwargs:
                try:
                    
                    trans = translations.get( language = TLanguage.objects.get( short = kwargs["lang"] ) )
                    data["place"] = trans.translate( data["place"] )
                    data["translated"] = True
                except Translation.DoesNotExist as e :
                    data["translated"] = False
                    data["message"] = "There is no translation in your language"
            else:
                data["translations"] = translations
                
            if data["place"].blocked and not ( data["place"].author == request.user and data["place"].inModeration):
                data = { "MEDIA_URL" : MEDIA_URL, "user": request.user, "message" : "The content is blocked." }
                return render_to_response( "message.html", data )
            if request.user.is_authenticated():
                meta = UserMetaData.objects.get( user = request.user )
                if meta.language != CONTENT_LANGUAGE_CODE and not "lang" in kwargs:
                    kwargs["lang"] = meta.language
                c = meta.observedContent.filter( id = data["place"].id ).count()
                if c > 0:
                    data["observed"] = True
                else:
                    data["observed"] = False
                vote = Vote.objects.get( votingUser = request.user, content = data["place"] )
                data["user"] = request.user
            else: 
                data["user"] = None
                vote = None
            if vote is not None:
                data["like"] = int( vote.promotion )
            else:
                data["like"] = False
           
            data["articles"] = [] 
            articles = data["place"].article_set.all()[:PAGE_ARTICLES]
            for art in articles:
                if not art.blocked or ( art.author == request.user and art.inModeration ):
                    data["articles"].append( art )
            
            for article in  data["articles"]:
                article.comment_form = CommentForm( initial = { "content" : article }).as_p()
            data["gallery"] = data["place"].getGallery()[:PAGE_PHOTOS]
            
            data.update( csrf(request) )
            return render_to_response( self.template_name, data )
        except Place.DoesNotExist as e:
            raise Http404()

class PlaceListView( ListView ):
    model = Place
    template_name = "places/places.html"
    def get(self, request, *args, **kwargs):
        data = { "MEDIA_URL" : MEDIA_URL }
        _list = Place.objects.all()
        data["list"] = []
        for item in _list:
            if item.type != "trans":
                if not item.blocked:
                    data["list"].append( item )
        
        data["user"] = request.user
        data["promoted"] = Place.objects.promoted()
        data["short"] = True
        data.update( csrf(request) )
        return render_to_response( self.template_name, data )

class ArticleListView( ListView ):
    model = Article
    template_name = "templates/places/articles.html"
    def get(self, request, *args, **kwargs):
        return ListView.get(self, request, *args, **kwargs)
    
class ArticleView( View ):
    def dispatch(self, request, *args, **kwargs):
        return View.dispatch(self, request, *args, **kwargs)
    
class PhotoListView( ListView ):
    model = Photo
    template_name = "templates/places/gallery.html"
    def get(self, request, *args, **kwargs):
        return ListView.get(self, request, *args, **kwargs)
    
class PhotoView( View ):
    def dispatch(self, request, *args, **kwargs):
        return View.dispatch(self, request, *args, **kwargs)
    
class CreatePlaceView( FormView ):
    form_class = PlaceForm
    def getForm(self, request, *args, **kwargs ):
        if request.POST:
            return self.form_class( request.POST , request.FILES )
        else:
            return self.form_class()
    def get(self, request, *args, **kwargs):      
        form = PlaceForm()
        data =  {
                 'multi' : True,
                 'form' : form.as_p(),
                 'user' : request.user
                 }
        data.update( csrf( request ) )
        return render_to_response( "staticform.html", data)
    def post(self, request, *args, **kwargs):
        
        form = self.getForm( request , *args, **kwargs )
        if form.is_valid():
            cdata = form.cleaned_data
            photo_data = cdata['photo']
            del cdata['photo']
            place = Place( 
                          title = cdata['title'],
                          author = request.user,
                          where = cdata['where'],
                          province = cdata['province'],
                          lead = cdata['lead']
                          )
            place.save()
            place.categories = cdata['categories']
            place.save() 
            Photo.objects.create( 
                                 image = photo_data, 
                                 place = place, 
                                 author = request.user, 
                                 title = cdata['photo_title'], 
                                 description = cdata['photo_description'] 
                                 )
            place.invokeEvent( request.user, 
                               description = "created new place: %s" %  place.title,
                               url = '/places/place,%s,%d.html' % ( place.title, place.id ) )
            return HttpResponseRedirect( '/places/place,%s,%d.html' % ( place.title, place.id ) ) 
        else:
            data =  {
                 'multi' : True,
                 'form' : form.as_p(),
                 'user' : request.user
                 }
            data.update( csrf( request ) )
            return render_to_response( "staticform.html", data)
            
class EditPlaceView( FormView ):
    def get(self, request, *args, **kwargs):
        place = Place.objects.get( id = kwargs["id"])
        if place.author == request.user:
            form = PlaceEditForm( instance = place )
            print form
            data =  {
                 'MEDIA_URL' : MEDIA_URL,
                 'form' : form,
                 'user' : request.user,
                 #"action" : "/places/edit,%d.html" % place.id
                 }
            data.update( csrf( request ) )
            return render_to_response( "staticform.html", data)
        else:
            return HttpResponseNotAllowed()
        
    def post(self, request, *args, **kwargs):
        form = PlaceEditForm( request.POST )
        if form.is_valid():
            place = form.save( commit = False )
            #Place.objects.filter( id = place.id ).update( place )
            old = Place.objects.get( id = kwargs["id"])
            old.title = place.title
            old.where = place.where
            old.province = place.province
            old.lead = place.lead
            old.save()
            place = old
            data =  {
                 'MEDIA_URL' : MEDIA_URL,
                 'user' : request.user
            }
            place.invokeEvent( request.user, 
                               description = "edited place: %s"%   place.title ,
                               url = '/places/place,%s,%d.html' % ( place.title, place.id ) )
            return HttpResponseRedirect( '/places/place,%s,%d.html' % ( place.title, place.id ) )
        else:
            data =  {
                 'MEDIA_URL' : MEDIA_URL,
                 'user' : request.user,
                 "form" : form
            }
            return render_to_response( "staticform.html", data)
        

class CreatePlaceContentView( FormView ):
    template_name = "staticform.html"
    form_class = None
    def get(self, request, *args, **kwargs):
        form = self.form_class( initial = { "place" : Place.objects.get( id = kwargs["id"] ) } )
        data = {
                "MEDIA_URL": MEDIA_URL,
                "user" : request.user,
                "form" : form,
                "multi" : True
                }
       
        data.update( csrf( request ) )
        return render_to_response( self.template_name, data )
    def post(self, request, *args, **kwargs):
        print "post"
        form = self.form_class( request.POST, request.FILES )
        if form.is_valid():
            c = form.save( commit = False )
            c.author = request.user
            c.save()
            c.invokeEvent( request.user, 
                           description = "created new place content: %s" %  c.title ,
                           url = '/places/place,%s,%d.html'.format ( unicode( c.place.title ) , int( c.place.id ) ) )
            return HttpResponseRedirect( "/places/place,%s,%d.html" % ( c.place.title, c.place.id ) )
        else:
            data = {
                "MEDIA_URL": MEDIA_URL,
                "user" : request.user,
                "form" : form,
                "multi" : True
            }
            data.update( csrf( request ) )
            return render_to_response( self.template_name, data )

class EditArticleView( FormView ):
    def get(self, request, *args, **kwargs):
        art = Article.objects.get( id = kwargs["id"])
        if art.author == request.user:
            form = ArticleEditForm( instance = art )
            
            data =  {
                 'MEDIA_URL' : MEDIA_URL,
                 'form' : form,
                 'user' : request.user,
                 #"action" : "/places/edit,%d.html" % place.id
                 }
            data.update( csrf( request ) )
            return render_to_response( "staticform.html", data)
        else:
            return HttpResponseNotAllowed()
        
    def post(self, request, *args, **kwargs):
        form = ArticleEditForm( request.POST )
        if form.is_valid():
            art = form.save( commit = False )
            #Place.objects.filter( id = place.id ).update( place )
            old = Article.objects.get( id = kwargs["id"])
            old.title = art.title
            old.content = art.content
            old.save()
            art = old
            data =  {
                 'MEDIA_URL' : MEDIA_URL,
                 'user' : request.user
            }
            art.invokeEvent( request.user, 
                               description = "edited article: %s"%  art.title ,
                               url = '/places/place,%s,%d.html' % ( art.place.title, art.place.id ) )
            return HttpResponseRedirect( '/places/place,%s,%d.html' % ( art.place.title, art.place.id ) )
        else:
            data =  {
                 'MEDIA_URL' : MEDIA_URL,
                 'user' : request.user,
                 "form" : form
            }
            return render_to_response( "staticform.html", data)
                       
                       
class EditPhotoView( FormView ):
    def get(self, request, *args, **kwargs):
        photo = Photo.objects.get( id = kwargs["id"])
        if photo.author == request.user:
            form = PhotoEditForm( instance = photo )
            
            data =  {
                 'MEDIA_URL' : MEDIA_URL,
                 'form' : form,
                 'user' : request.user,
                 #"action" : "/places/edit,%d.html" % place.id
                 }
            data.update( csrf( request ) )
            return render_to_response( "staticform.html", data)
        else:
            return HttpResponseNotAllowed()
        
    def post(self, request, *args, **kwargs):
        form = PhotoEditForm( request.POST )
        if form.is_valid():
            photo = form.save( commit = False )
            #Place.objects.filter( id = place.id ).update( place )
            old = Photo.objects.get( id = kwargs["id"])
            old.title = photo.title
            old.description = photo.description
            old.save()
            photo = old
            data =  {
                 'MEDIA_URL' : MEDIA_URL,
                 'user' : request.user
            }
            photo.invokeEvent( request.user, 
                               description = "edited photo: %s"%  photo.title ,
                               url = '/places/place,%s,%d.html' % ( photo.place.title, photo.place.id ) )
            return HttpResponseRedirect( '/places/place,%s,%d.html' % ( photo.place.title, photo.place.id ) )
        else:
            data =  {
                 'MEDIA_URL' : MEDIA_URL,
                 'user' : request.user,
                 "form" : form
            }
            return render_to_response( "staticform.html", data)
class UrlPlaceListView( View ):
    template_name = "list.html" 
    title = None  
    def dispatch(self, request, *args, **kwargs):
        data = {
                "MEDIA_URL" : MEDIA_URL,
                "user" : request.user,
            
                }
        _list = Place.objects.filter( author = request.user )
        data["short"] = True
        data["list"] = []
        for item in _list:
            #if item.type != "trans":
            if not item.blocked or item.inModeration:
                data["list"].append( ( item.title, "/places/place,%s,%d.html" % (item.title, item.id ), item.author, item.datePublish ) )
        if self.title is not None:
            data["title"] = self.title
        return render_to_response( self.template_name , data )   
  
class PublishedView( View ):
    template_name = None
    model = None
    def dispatch(self, request, *args, **kwargs):
        data = {
                "MEDIA_URL": MEDIA_URL,
                "user" : request.user,
               
            }
        _list = self.model.objects.filter( author = request.user )
        data["list"] = []
        for item in _list:
            if item.type != "trans":
                if not item.blocked or item.inModeration:
                    data["list"].append( item )
        
        return render_to_response( self.template_name, data )
