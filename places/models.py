# -*- coding: utf-8 -*-
from django.db import models
from core.models import Content, Translation, TLanguage
from ePolonica.settings import UPLOAD_TO
from django.contrib import admin
from core.managers import ContentManager
from django.db.models.signals import post_save
from search.signals import  search_register

# Create your models here.
provinces = ( ("Podkarpackie", "Podkarpackie"),)
class PlaceCategory( models.Model ):
    """
    Kategoria miejsca, może być np. muzea, miasta, natura etc.
    """
    name = models.CharField( max_length = 255 )
    description = models.CharField( max_length = 1024 )
    def __unicode__(self):
        return self.name
class Place( Content ):
    """
    Model reprezentujący pojedyncze miejsce
    """
    translation = False
    #photo = models.ForeignKey( "Photo", related_name = "place_main" )
    where = models.CharField( max_length = 1024 )
    province = models.CharField( max_length = 64, choices = provinces )
    categories = models.ManyToManyField( "PlaceCategory" , null = True, blank = True )
    lead = models.CharField( max_length = 1024 )
    related = models.ManyToManyField( "Place", null = True, blank = True )
    visited = models.IntegerField( max_length = 11, default = 0 )
    objects = ContentManager()
    def setPhoto(self, photo ):
        self.photo = photo
    def getGallery(self):
        return self.gallery_photo.filter( blocked = False )
class Article( Content ):
    '''
    Model reprezentuje pojedynczy artykuł związwany z miejscem.
    '''
    content = models.TextField()
    place = models.ForeignKey( "Place" )
    objects = ContentManager()


class Photo( Content ):
    image = models.ImageField( upload_to = UPLOAD_TO + "places/" )
    description = models.CharField( max_length = 1024 )
    place = models.ForeignKey( "Place", related_name = "gallery_photo" )
    objects = ContentManager()
    
class PhotoTranslation( Translation ):
    description = models.CharField( max_length = 1024 )
    related_content = models.ForeignKey( Photo, related_name = "translations" )
class ArticleTranslation( Translation ):
    content = models.TextField()
    related_content = models.ForeignKey( Article, related_name = "translations" )
class PlaceTranslation( Place ):
    translation = True
    language = models.ForeignKey( TLanguage )
    related_content = models.ForeignKey( Place, related_name = "translations" )
    
    def translate(self, item ):
        return self
    def getGallery(self):
        return self.related_content.gallery_photo.filter( blocked = False )
admin.site.register( Article )
admin.site.register( PlaceCategory )
admin.site.register( Place )
admin.site.register( PlaceTranslation )
admin.site.register( Photo )
post_save.connect( search_register, sender = Article )
post_save.connect( search_register, sender = Photo )


