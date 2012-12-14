from django.db import models
from ePolonica.settings import UPLOAD_TO, MEDIA_URL
from managers import CaptchaManager
from django.contrib import admin
from django.utils.safestring import mark_safe
from httplib import HTTPResponse
from django.contrib.auth.models import User
# Create your models here.
class Captcha( models.Model ):
    image = models.ImageField( upload_to = UPLOAD_TO + "captcha/" )
    code = models.CharField( max_length = 8 )
    objects = CaptchaManager() 
    def getPublicUrl(self):
        return MEDIA_URL + self.image.name
    def asHtml(self):
        return mark_safe( '<img src="%s" alt="captcha" />' % self.getPublicUrl() ) 
    def __unicode__(self):
        return self.code
    
    
class Activation( models.Model ):
    code = models.CharField( max_length = 255 )
    user = models.ForeignKey( User )
    timeout = models.DateTimeField()
admin.site.register( Captcha )