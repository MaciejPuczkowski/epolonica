# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib import admin

from ePolonica.settings import UPLOAD_TO, LANGUAGE_CODE, MEDIA_URL
from core.managers import CaptchaManager, VoteManager, ContentManager
from django.utils.safestring import mark_safe
import managers
languages = (
             ("English","en-En"),
             )
class UserEvent( models.Model ):
    time = models.DateTimeField( default = datetime.now() )
    description = models.CharField( max_length = 255 )
    url = models.CharField( max_length = 255, null = True, blank = True  )
    user = models.ForeignKey( User )
    def __unicode__(self):
        return unicode( self.time ) + " " + unicode( self.user ) + ": " + self.description 


    

    
class Content( models.Model ):
    title = models.CharField( max_length = 255 )
    datePublish = models.DateTimeField( default = datetime.now() )
    lastModifiedDate = models.DateTimeField( default = datetime.now() )
    author = models.ForeignKey( User, related_name = "content_authors_set" )
    type = models.CharField( max_length = 64 )
    objects = ContentManager( )
    #observers = models.ManyToManyField( User, null = True, blank = True )
    blocked = models.BooleanField( default = False )
    inModeration = models.BooleanField( default = False )
    rank = 0
    
    def invokeEvent(self, user, description, url = "#" ):
        UserEvent.objects.create( user = user, description = description, url = url )
        
    def __unicode__(self):
        return self.title
    
class Translation( models.Model ):
    """
    Klasa abstrakcyjna, klasy dziedziczące powinny dopisać pole "content",
    które wskazywałoby na tłumaczony obiekt.
    """
    language = models.ForeignKey( "TLanguage" )
    

class Comment( models.Model ):
    author = models.ForeignKey( User )
    text = models.TextField()
    content = models.ForeignKey( "Content" )
    date = models.DateTimeField()

    def __unicode__(self):
        if len( self.text ) > 100:
            text = self.text[:100] + "..."
        else:
            text = self.text
        return self.content.title + ": " + text
    
class Address( models.Model ):
    user = models.ForeignKey( User )
    city = models.CharField( max_length = 255, null = True, blank = True )
    street = models.CharField( max_length = 255, null = True, blank = True )
    postalCode = models.CharField( max_length = 64, null = True, blank = True )
    houseNo = models.CharField( max_length = 8, null = True, blank = True )
    flatNo = models.CharField(max_length = 8, null = True, blank = True )
    hide = models.BooleanField( default = False )
    def __unicode__(self):
        return unicode( self.user )
class Photo(models.Model):
    image = models.ImageField( upload_to = "profiles/photo/")
    user = models.ForeignKey( User) 
    def asHtml(self):
        raise NotImplemented()
    def getPublicUrl(self):
        raise NotImplemented()   
class UserMetaData( models.Model ):
    blocked = models.BooleanField( default = False )
    canComment = models.BooleanField( default = True )
    removed = models.BooleanField( default = False )
    mailboxLastVisit = models.DateTimeField( default = datetime.now() )
    language = models.ForeignKey( "TLanguage", blank = True, null = True )
    user = models.ForeignKey( User )
    observers = models.ManyToManyField( User , related_name = "user_observers", null = True, blank = True )
    observedUsers = models.ManyToManyField( User , related_name = "user_observed_user", null = True, blank = True )
    observedContent = models.ManyToManyField( "Content", related_name = "user_observed_content" , null = True, blank = True )
    def __unicode__(self):
        return unicode( self.user )
    
class Message( models.Model ):
    title = models.CharField( max_length = 255 )
    users = models.ManyToManyField( User )
    author = models.ForeignKey( User, related_name = "message_authors_set" )
    date = models.DateTimeField()
    text = models.TextField()
    objects = managers.MessageManager()
    def __unicode__(self):
        return self.title
class Response( models.Model ):
    text = models.TextField()
    author = models.ForeignKey( User )
    date = models.DateTimeField( default = datetime.now() )
    message = models.ForeignKey( "Message" )
    def __unicode__(self):
        message = self.message.split(" ")[:50].join(" ")
        return unicode( self.author ) + ": " + message + "..."
#@todo:  to project
class TLanguage( models.Model ):
    short = models.CharField( max_length = 4 )
    long = models.CharField( max_length = 32 )
    icon = models.ImageField( upload_to = UPLOAD_TO + "icons/languages/" ) 
    def __unicode__(self):
        return self.long





class ReportReason( models.Model ):
    text = models.CharField( max_length = 1024 )
    def __unicode__(self):
        return self.text
    
class ErrorType( models.Model ):
    text = models.CharField( max_length = 1024 )
    def __unicode__(self):
        return self.text
    
class Report( models.Model ):
    author = models.ForeignKey( User )
    date = models.DateTimeField( default = datetime.now() )
    comment = models.TextField()

    status = models.CharField( max_length = 8 , choices = (
                                                           ("in progres", "in progres"),
                                                           ("done" , "done"),
                                                           ("impossible", "impossible" ),
                                                           ("later", "later"),
                                                           ("new", "new")
                                                           ),
                              default = "new"
                              )
    closingComment = models.TextField()
    def __unicode__(self):
        return "Date: %s Author: %s Status: %s Text: %s" % ( unicode( self.date ), self.author, self.status , self.comment  )
    
class ReportContent( Report ):
    reason = models.ForeignKey( "ReportReason" )
    content = models.ForeignKey( "Content" )
    
class ReportUser( Report ):
    reason = models.ForeignKey( "ReportReason" )
    user = models.ForeignKey( User )
    
class ReportError( Report ):
    type = models.ForeignKey( "ErrorType" )

class Vote( models.Model ):
    promotion = models.BooleanField( default = True )
    votingUser = models.ForeignKey( User )
    content = models.ForeignKey( "Content" )
    objects = VoteManager()
    
    
# Create your models here.
class Captcha( models.Model ):
    image = models.ImageField( upload_to = "captcha/" )
    code = models.CharField( max_length = 8 )
    objects = CaptchaManager() 
    def getPublicUrl(self):
        return MEDIA_URL + self.image.name
    def asHtml(self):
        return mark_safe( '<img src="%s" alt="captcha" width="300px" >' % self.getPublicUrl() ) 
    def __unicode__(self):
        return self.code
    
    
class Activation( models.Model ):
    code = models.CharField( max_length = 255 )
    user = models.ForeignKey( User )
    timeout = models.DateTimeField()


admin.site.register( TLanguage )  
admin.site.register( Captcha )    
admin.site.register( Activation ) 
admin.site.register( UserMetaData )
admin.site.register( Photo ) 
admin.site.register( Content )
admin.site.register( ReportContent )
admin.site.register( ReportUser )
admin.site.register( ReportError )
admin.site.register( Vote )
admin.site.register( ErrorType )
admin.site.register( ReportReason )
admin.site.register( UserEvent )
admin.site.register( Message )
admin.site.register( Response )
admin.site.register( Address )
admin.site.register( Comment )
    