# -*- coding: utf-8 -*-
from django.views.generic.edit import FormView
from django.views.generic.base import View
from ePolonica.settings import MEDIA_ROOT
from django.contrib import staticfiles

class AuthoredView( FormView ):
    """
    Can receive form for model with fields "author" and "date" which are got from session.
    Class can be used for any data which are put by users. It assumes that other required data
    are in form.
    """
    def get(self, request, *args, **kwargs):
        return FormView.get(self, request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)
#@todo: to project
class AuthoredUploadingView( AuthoredView ):
    """
    Class is dedicated for Authored data with uploading field
    """
    pass
    
class UserView( FormView ):
    """
    Can receive form for model with field named "user", and this "user"
    is not got by form but session.
    """
    def get(self, request, *args, **kwargs):
        return FormView.get(self, request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)
    
class CreateContentView( FormView ):
    def get(self, request, *args, **kwargs):
        return FormView.get(self, request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)

class EditContentView( FormView ):
    def get(self, request, *args, **kwargs):
        return FormView.get(self, request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)

class VoteContentView( FormView ):
    def get(self, request, *args, **kwargs):
        return FormView.get(self, request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)
    


def MediaView( request, path ):
    print path
    print MEDIA_ROOT + path
    return staticfiles.views.serve(request, path, document_root = MEDIA_ROOT )  
    