# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib import admin
import managers
from ePolonica.settings import UPLOAD_TO
class Content( models.Model ):
    title = models.CharField( max_length = 255 )
    datePublish = models.DateTimeField( default = datetime.now() )
    lastModiefiedDate = models.DateTimeField( default = datetime.now() )
    author = models.ForeignKey( User, related_name = "content_authors_set" )
    type = models.CharField( max_length = 64 )
    objects = managers.ContentManager()
    observers = models.ManyToManyField( User, null = True, blank = True )
    def __unicode__(self):
        return self.title
    
class Comment( models.Model ):
    author = models.ForeignKey( User )
    text = models.TextField()
    content = models.ForeignKey( "Content" )
    date = models.DateTimeField()
    objects = managers.CommentManager()
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
#@todo:  to project
class Language( models.Model ):
    short = models.CharField( max_length = 4 )
    long = models.CharField( max_length = 32 )
    icon = models.ImageField( upload_to = UPLOAD_TO + "icons/languages/" ) 
    def __unicode__(self):
        return self.long
#@todo:  to project
class Translation( models.Model ):
    content = models.ForeignKey( "Content" )
    language = models.ForeignKey( "Language" )
    
class Response( models.Model ):
    message = models.ForeignKey( "Message" )
    text = models.TextField()

class UserEvent( models.Model ):
    time = models.DateTimeField()
    type = models.CharField( max_length = 64 )
    description = models.CharField( max_length = 255 )
    user = models.ForeignKey( User )
    objects = managers.EventManager()
    

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
    date = models.DateTimeField()
    comment = models.TextField()
    objects = managers.ReportManager()
    
class ReportContent( Report ):
    reason = models.ForeignKey( "ReportReason" )
    content = models.ForeignKey( "Content" )
    
class ReportUser( Report ):
    reason = models.ForeignKey( "ReportReason" )
    user = models.ForeignKey( User )
    
class ReportError( Report ):
    type = models.ForeignKey( "ErrorType" )

class Vote( models.Model ):
    promotion = models.BooleanField()
    votingUser = models.ForeignKey( User )
    objects = managers.VoteManager()
    votedContent = models.ForeignKey( "Content" )
    
admin.site.register( Content )
admin.site.register( ReportContent )
admin.site.register( ReportUser )
admin.site.register( ReportError )

admin.site.register( ErrorType )
admin.site.register( ReportReason )
admin.site.register( UserEvent )
admin.site.register( Message )
admin.site.register( Address )
admin.site.register( Comment )
    