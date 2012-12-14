# -*- coding: utf-8 -*-
from django.db import models
from core.models import Content
from ePolonica.settings import UPLOAD_TO
from django.contrib import admin
# Create your models here.
provinces = ( )
class PlaceCategory( models.Model ):
    name = models.CharField( max_length = 255 )

class Place( Content ):
    where = models.CharField( max_length = 1024 )
    province = models.CharField( max_length = 64, choices = provinces )
    categories = models.ManyToManyField( "PlaceCategory" )
    related = models.ManyToManyField( "Place", null = True, blank = True )
    
class Article( Content ):
    content = models.TextField()
    place = models.ForeignKey( "Place" )


class Photo( Content ):
    image = models.ImageField( upload_to = UPLOAD_TO + "places/" )
    description = models.CharField( max_length = 1024 )
    place = models.ForeignKey( "Place" )
    
admin.site.register( Article )
admin.site.register( PlaceCategory )
admin.site.register( Place )
admin.site.register( Photo )

