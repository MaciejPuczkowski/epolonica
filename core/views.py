
# -*- coding: utf-8 -*-
from django.views.generic.edit import FormView
from django.views.generic.base import View
from ePolonica.settings import MEDIA_ROOT, EMAIL_HOST_USER, MEDIA_URL, TIME_ZONE
from django.contrib import staticfiles
from datetime import datetime, timedelta
from core.models import Captcha, Activation, Vote, UserEvent, UserMetaData,\
    Address, Photo, Content, Message, Comment, Translation
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from core.forms import RegisterForm, MessageForm, ResponseForm, CommentForm,\
    AddressForm, ProfilePhotoForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponseNotFound, HttpResponseRedirect, HttpResponse
from multiprocessing.managers import dispatch
from django.views.generic.list import ListView
from django.utils.decorators import classonlymethod
from django.template import loader
from django.template.context import Context
from django.core.signing import Signer
from django.contrib.sites.models import Site
from datetime import datetime

import time
from django.utils.timezone import utc,now
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
                   
class AuthoredFormView( FormView ):
    """
    Model obsługuje dowolny formularz posiadający pole author przypisując mu
    wartość request.user. Dziedzicząc  po nim i przeciążając metodę getInitial()
    można nadac początkowe wartości formularzowi. Parametr form_class jest obslugiwanym formularzem.
    """
    model = None
    form_class = None
    template_name = "staticform.html"
    template_name_async = "form.html"
    def getInitial(self, request, *args, **kwargs ):
        return {}
    @method_decorator( login_required )
    def get(self, request, *args, **kwargs):
        form = self.form_class( initial = self.getInitial(request, *args, **kwargs) )
        data = {
                "MEDIA_URL" : MEDIA_URL,
                "user" : request.user,
                "form" : form
                }
        data.update( csrf(request) )
        template = self.template_name
        return render_to_response( template, data )
    
    @method_decorator( login_required )
    def post(self, request, *args, **kwargs):
        form = self.form_class( request.POST, request.FILES )
        data = {
                "MEDIA_URL" : MEDIA_URL,
                "user" : request.user,
                "form" : form
                }
        if form.is_valid():
            obj = form.save( commit = False )
            obj.author = request.user
            obj.save()
            return HttpResponseRedirect( self.success_url )
        else:
            data.update( csrf(request) )
            template = self.template_name
            return render_to_response( template, data ) 

class ReportUserView( AuthoredFormView ):
    """
    Model obsługujący zgłoszenia naruszenia regulaminu przez użytkownika
    """
    def getInitial(self, request, *args, **kwargs):
        return { "user" : User.objects.get( id = kwargs["id"] ) }
class ReportContentView( AuthoredFormView ):
    """
    Model sbsługujący zgłoszenia naruszenia regulaminu w materiale.
    """
    def getInitial(self, request, *args, **kwargs):
        return { "content" : Content.objects.get( id = kwargs["id"] ) }
    
class MessageListView( View ):
    """
    Zwraca listę wiadomości - mailbox.
    """
    @method_decorator( login_required )
    def dispatch(self, request, *args, **kwargs):
        data = {
                "MEDIA_URL" : MEDIA_URL,
                "user" : request.user,
                "list" : request.user.message_set.all().order_by("-date"),
                "short": True
                }
        return render_to_response( "core/messages.html", data )
class MessageView( View ):
    """
    Widok pojedynczej wiadomości
    """
    template_name = None
    @method_decorator( login_required )
    def dispatch(self, request, *args, **kwargs):
        msg = Message.objects.get( id = kwargs["id"] )
        data = {
                "MEDIA_URL" : MEDIA_URL,
                "user" : request.user,
                "msg" : msg,
                "responses" : msg.response_set.all()[:10],
                "form": ResponseForm( initial = { "message" : msg } ),
                "short": True
                }
        print dir( msg )
        data.update( csrf( request ) )
        return render_to_response( self.template_name, data )
           
class MessageCreateView( FormView ):
    template_name = "staticform.html"
    @method_decorator( login_required )
    def get(self, request, *args, **kwargs):
        form = MessageForm()
        data = {
                "MEDIA_URL" : MEDIA_URL,
                "user" : request.user,
                "form" : form
                }
        data.update( csrf( request ) )
        return render_to_response( self.template_name, data )
    @method_decorator( login_required )
    def post(self, request, *args, **kwargs):
        form = MessageForm( request.POST )
        if form.is_valid():
            data = form.cleaned_data
            users_t = data["users"].split(",")
            message = Message( 
                              author = request.user, 
                              text = data["text"],
                              title = data["title"],
                              date = datetime.now()
                              )
            message.save()
            message.users.add( request.user )
            for user in users_t:
                user = user.strip()
                try:
                    if user != request.user.username:
                        message.users.add( User.objects.get( username = user ) )
                except User.DoesNotExist as e:
                    print user + " does not exist." 
            message.save()
            return HttpResponseRedirect("/mailbox/list.html" )
        else:
            data = {
                "MEDIA_URL" : MEDIA_URL,
                "user" : request.user,
                "form" : form
                }
            data.update( csrf( request ) )
            return render_to_response( self.template_name, data )
class RespondView( FormView ):
    @method_decorator( login_required )
    def post(self, request, *args, **kwargs):
        form = ResponseForm( request.POST )
        if form.is_valid():
            msg = form.save( commit = False )
            msg.author = request.user
            msg.save()
        return HttpResponseRedirect("/mailbox/message,%d,html" % int( kwargs["id"] ) )
      
class UserFormView( FormView ):
    """
    Can receive form for model with field named "user", and this "user"
    is not got by form but session.
    """
    model = None
    @method_decorator( login_required )
    def get(self, request, *args, **kwargs):
        return FormView.get(self, request, *args, **kwargs)
    @method_decorator( login_required )
    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)
    


class VoteContentView( View ):
    @method_decorator( login_required )
    def dispatch(self, request, *args, **kwargs):
        if Vote.objects.vote( kwargs["id"], request.user ):
            return HttpResponse( "Unlike" )
        else:
            return HttpResponse( "Like" )
    
class ProfileView( View ):
    @method_decorator( login_required )
    def dispatch(self, request, *args, **kwargs):
        meta = UserMetaData.objects.get( user = request.user )
        if not request.POST: address = AddressForm( instance = Address.objects.get( user = request.user ) )
        if not request.POST: pform = ProfilePhotoForm()
        try:
            photo = Photo.objects.get( user = request.user )
        except: 
            photo = None 
        if request.POST:
            if request.GET[ "f" ] == "a":
                address = AddressForm( request.POST )
                pform = ProfilePhotoForm()
                if address.is_valid():
                    obj = address.save( commit = False )
                    Address.objects.filter( user = request.user ).update( 
                                                                            city = obj.city,
                                                                            street = obj.street,
                                                                            postalCode = obj.postalCode,
                                                                            houseNo = obj.houseNo,
                                                                            flatNo = obj.flatNo,
                                                                            hide = obj.hide
                                                                         )
                else:
                    address = AddressForm( instance = Address.objects.get( user = request.user ) )
        
            elif request.GET[ "f" ]  == "p":
                address = AddressForm( instance = Address.objects.get( user = request.user ) )
                pform = ProfilePhotoForm( request.POST, request.FILES )
                print "ppp"
                if pform.is_valid():
                    print "valid"
                    obj = pform.save( commit = False )
                    Photo.objects.filter( user = request.user ).delete()
                    obj.user = request.user
                    obj.save()
                    photo = obj
                else:
                    pform = ProfilePhotoForm()
            else:
                address = AddressForm( instance = Address.objects.get( user = request.user ) )
                pform = ProfilePhotoForm()
        
        data = {
             "MEDIA_URL" : MEDIA_URL,
             "user" : request.user,
             "private" : True,
             "address" : address,
             "meta" : meta,
             "photo" : photo,
             "photo_form" :pform,
             "short": True
             }
        data.update( csrf( request ) )
        return render_to_response( "core/panel.html", data )
class PublicProfileView( View ):
    @method_decorator( login_required )
    def dispatch(self, request, *args, **kwargs):
        user = User.objects.get( id = kwargs["id"] )
        meta = UserMetaData.objects.get( user = user )
        address = Address.objects.get( user = user )
        try:
            photo = Photo.objects.get( user = user )
        except:
            photo = None
        if meta.observedUsers.filter( id = user.id ).count() > 0:
            observed = True
        else:
            observed = False
        data = {
             "MEDIA_URL" : MEDIA_URL,
             "user" : user,
             "private" : False,
             "address" : address,
             "meta" : meta,
             "observed" : observed,
             "photo" : photo
             }
        return render_to_response( "core/panel.html", data )
class ObservingUsersView( View ):
    @method_decorator( login_required )
    def dispatch(self, request, *args, **kwargs):
        list = UserMetaData.objects.get( user = request.user ).observers.all()
        data = {
                "MEDIA_URL" : MEDIA_URL,
                "user" : request.user,
                "list" : list,
                "short": True
                }
        return render_to_response( "core/users.html" , data )
class ObservedUsersView( View ):
    @method_decorator( login_required )
    def dispatch(self, request, *args, **kwargs):
        list = UserMetaData.objects.get( user = request.user ).observedUsers.all()

            
        data = {
                "MEDIA_URL" : MEDIA_URL,
                "user" : request.user,
                "list" : list,
                "short" : True
                }
        
        return render_to_response( "core/users.html" , data )
class ObservedContentsView( View ):
    model = None
    template_name = None
    @method_decorator( login_required )
    def dispatch(self, request, *args, **kwargs):
        _list = UserMetaData.objects.get( user = request.user ).observedContent.all()
        data = data = {
                "MEDIA_URL" : MEDIA_URL,
                "user" : request.user,
                "list" : [],
                "short" : True
                }
        print _list
        for item in _list:
            try:
                data["list"].append( self.model.objects.get( id = item.id ) )
            except self.model.DoesNotExists as e:
                pass
        print data["list"]
        return render_to_response( self.template_name, data )
class ObserveUser( View ):
    def dispatch(self, request, *args, **kwargs):
        user = User.objects.get( id = kwargs["id"] )
        meta = UserMetaData.objects.get( user = request.user )
        list = meta.observedUsers.all()
        
        found = False
        for item in list:
            if user.id == item.id:
                found = True
                break
        if found:
            meta.observedUsers.remove( user )
            UserMetaData.objects.get( user = user ).observers.remove( User.objects.get( id = request.user.id ) )
            return HttpResponse( "Observe" )
        else:
            meta.observedUsers.add( user )
            UserMetaData.objects.get( user = user ).observers.add( User.objects.get( id = request.user.id ) )
            return HttpResponse( "Stop observing" )
class ObserveContent( View ):
    @method_decorator( login_required )
    def dispatch(self, request, *args, **kwargs):
        meta = UserMetaData.objects.get( user = request.user )
        c = Content.objects.get( id = kwargs["id"] )
        contents = meta.observedContent.all()
        found = False
        for content in contents:
            if content.id == c.id :
                found = True
                break
        if found:
            meta.observedContent.remove( c )
            return HttpResponse( "Observe" )
        else:
            meta.observedContent.add( c )
            return HttpResponse( "Stop observing" )
        
class HistoryView( View ):
    @method_decorator( login_required )
    def dispatch(self, request, *args, **kwargs):
        data = { 
                "MEDIA_URL": MEDIA_URL,
                "user" : request.user,
                "list" : UserEvent.objects.filter( user = request.user ).order_by( "-time" )
                }
        return render_to_response( "core/events.html", data )
class EventsView( View ):
    template_name = "core/events.html"
    @method_decorator( login_required )
    def dispatch(self, request, *args, **kwargs):
        
        if "time" in kwargs:
            
            interv = True 
            if float( kwargs["time"] ) != 0:
                _time = datetime.fromtimestamp( float( kwargs["time"]  ) )
                
        else:
            interv = False
            
        meta = UserMetaData.objects.get( user = request.user )
        _list = []
        
        for u in meta.observedUsers.all():
            qset = UserEvent.objects.filter( user = u )
            
            if interv:
                
                if float ( kwargs["time"] ) == 0:
                    qset = qset.filter( time__gte = now() - timedelta( hours = 24 ) )
                    
                else: 
                    qset = qset.filter( time__gt = _time )
                    
            _list.extend( qset )
        
        sorted( _list , lambda a, b : a.time < b.time )
        data = { 
                "MEDIA_URL": MEDIA_URL,
                "user" : request.user,
                "list" : _list,
                "last_time" : time.mktime( datetime.now( ).utctimetuple() )
                }
        
        return render_to_response( self.template_name , data )
class ReactivationView( View ):
    def dispatch(self, request, *args, **kwargs):
        return View.dispatch(self, request, *args, **kwargs)
class CommentsView( View ):
    @method_decorator( login_required )
    def dispatch(self, request, *args, **kwargs):
        #@todo: Sprawdzic, czy uzytkownik moze komentowac
        meta = UserMetaData.objects.get( user = request.user )
        
        if request.POST and meta.canComment:
            form = CommentForm( request.POST )
            if form.is_valid():
                obj = form.save( commit = False )
                if obj.text.strip() == "":
                    return HttpResponse( 0 )
                obj.author = request.user
                obj.date = datetime.now()
                obj.save()
            else: 
                return HttpResponse( 0 )
        
        form = CommentForm( initial={"content" : Content.objects.get( id = kwargs["id"] ) })
        comments = Comment.objects.filter( content = Content.objects.get( id = kwargs["id"] ) )
        data = { 
                "MEDIA_URL": MEDIA_URL,
                "user" : request.user,
                "comments" :  comments,
                "form" : form,
                "id" : kwargs["id"]
                }
        data.update( csrf( request ) )
        return render_to_response( "core/comments.html", data )
         
class TranslateView( FormView ):
    model = None
    trans_model = None
    def invalid_form(self, request, form):
        data = { 
                    "MEDIA_URL": MEDIA_URL,
                    "user" : request.user,
                    "form" : form
                    }
        data.update( csrf( request ) )
        return render_to_response("staticform.html", data )
    @method_decorator( login_required )
    def get(self, request, *args, **kwargs):
        data = { 
                "MEDIA_URL": MEDIA_URL,
                "user" : request.user,
                }
        form = self.form_class( initial = { "related_content": self.model.objects.get( id = kwargs["id"]) } )
        data["form"] = form
        data.update( csrf( request ))
        return render_to_response("staticform.html", data )
    @method_decorator( login_required )   
    def post(self, request, *args, **kwargs):
        if "next" in kwargs:
            self.success_url = kwargs["next"]
        else:
            self.success_url = "/"
        form = self.form_class( request.POST )
        if form.is_valid():
            obj = form.save( commit = False )
            obj.author = request.user
            if self.trans_model.objects.filter( related_content = obj.related_content, language = obj.language ).count() > 0:
                form.errors["language"] = [ "Translation exists." ]
                return self.invalid_form( request, form ) 
            obj.type = "trans"
            obj.save()
            return HttpResponseRedirect( self.success_url )
        else:
            return self.invalid_form( request, form )
        

activation_timeout = timedelta( days = 7 )
LOCALHOST = "http://localhost:8000"

class RegistrationView( FormView ):
    success_url = "/"
    def invalid(self, form, request, message = None ):
        captcha = Captcha.objects.get( id = int( form.data["captcha_id" ] ) )
        data = { "form" : form.as_p(), 'captcha': captcha.asHtml() }
        data.update( csrf( request ) )
        return render_to_response("regform.html", data )
    def get(self, request, *args, **kwargs):
        captcha = Captcha.objects.get()
        form = RegisterForm( initial = {"captcha_id" : captcha.id } )
        data = { "form" : form.as_p(), 'captcha': captcha.asHtml() }
        data.update( csrf( request ) )
        return render_to_response("regform.html", data )
    def post(self, request, *args, **kwargs):
        form = RegisterForm( request.POST )
        
        if form.is_valid():
            data = form.cleaned_data
            captcha = Captcha.objects.get( id = int( data["captcha_id" ] ) )
            
            if captcha.code != data["captcha"] or data["password"] != data["repassword"]:
                form.errors['captcha'] = ['Incorrect captcha']
                return self.invalid( form , request )
            if data["password"] != data["repassword"]:
                form.errors['password'] = ['Diffrent passwords']
                return self.invalid( form , request )
            if User.objects.filter( email = data["email"] ).count() > 0:
                form.errors['email'] =  ['Email already exists!']
                return self.invalid( form , request )
            
            if User.objects.filter( username = data["username"] ).count() > 0:
                form.errors['username'] = ['Username already exists']
                return self.invalid( form , request )
            del data["captcha"]
            del data["captcha_id"]
            del data["repassword"]
            data["is_active"] = False
            password = data["password"]
            del data["password"]
            user = User( **data )
            user.set_password( password )
            user.save()
            signer = Signer()
            code = signer.sign( user.username+user.first_name+user.last_name+user.email ).split(":")[1]
            Activation.objects.create( user = user, code = code, timeout = datetime.now() + activation_timeout )
            url = LOCALHOST + "/activate/" + str( user.id ) +"/" + code
            temp = loader.get_template("registration_mail.txt")
            activation_message = temp.render( Context( {
                                   "activation_url" : url,
                                   "respiration_time" : activation_timeout,
                                   "user" : user
                                   } ) )
                        
            send_mail(
                      "Activation",
                      activation_message, 
                      EMAIL_HOST_USER,
                      [user.email], fail_silently=False
                      )
            UserMetaData.objects.create( user = user )
            Address.objects.create( user = user )
            return render_to_response("registration_success.html", { "success_url": self.success_url })
        else:
            return self.invalid( form, request )
        
class ActivationView( View ):
    def dispatch(self, request, *args, **kwargs):
        try:
            
            code = kwargs["code"]
            id = kwargs["id"]
            user = User.objects.get( id = id )
            activs = Activation.objects.filter( user = user )
            ok_activs = activs.filter( timeout__gte = datetime.now() )
            found = False
            for oka in ok_activs:
                if oka.code == code:
                    user.is_active = True
                    user.save()
                    found = True
                    break
        except user.DoesNotExists as e:
            return HttpResponseNotFound()
        
        if found: 
            return render_to_response("activation.html", {"success_url" :"/"})    
        else:
            return HttpResponseNotFound()

class Redirection( View ):
    to = '/end'
    def dispatch(self, request, *args, **kwargs):
        print self.to
        return HttpResponseRedirect( self.to )
@login_required
def MediaView( request, path ):
    return staticfiles.views.serve(request, path, document_root = MEDIA_ROOT )  
    