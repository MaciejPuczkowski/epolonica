# -*- coding: utf-8 -*-
from django.views.generic.edit import FormView
from search.forms import SearchLine
from django.http import HttpResponse
from core.models import Content
import re
import string
from ePolonica.settings import MEDIA_URL
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
def plToAng(text):
    translate = {u'ą':'a', u'ć':'c', u'ę':'e', u'ł':'l', u'ń':'n', u'ó':'o', u'ś':'s', u'ż':'z', u'ź':'z'}
    newText = ''
    for c in text:
        if c in translate:
            c = translate[c]
        newText = newText + c
    return newText
class SearchContents( FormView ):
    template_name = None
    def post(self, request, *args, **kwargs):
        form = SearchLine( request.POST )
        if form.is_valid():
            line = string.lower( plToAng( form.cleaned_data["line"] ).strip() )
            line_i = line.split(" ")
            line = ""
            for i in line_i:
                line += i
            patterns = []
            patterns.append( ".*" + line + ".*" )
            for i in range(  len( line ) - 1  ):
                patterns.append( ".*" + line[:i] + line[i+1:] + ".*" )
            for a in range( 1, 3 ):
                for i in range(1,  len( line ) ):
                    patterns.append( ".*" + line[:i] +  ".{" + str( a ) + "}" + line[i:]+ ".*" )
            result = []
            contents = Content.objects.all()
            for pattern in patterns:
                #print "P: --> " + pattern
                for content in contents:
                    title = string.lower( plToAng( content.title ) )
                    title_i = title.split(" ")
                    title =""
                    for t in title_i:
                        title += t
                    if re.search( re.compile( pattern ) , title ) is not None and not content in result:
                        result.append( content )
                        
            data = { 
                    "MEDIA_URL" : MEDIA_URL,
                    "user" : request.user,
                    "list" : result
                      }
            data.update( csrf( request ) )
            return render_to_response( self.template_name , data )
        else: 
            return HttpResponse( False )