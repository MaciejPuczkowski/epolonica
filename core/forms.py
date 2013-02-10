# -*- coding: utf-8 -*-
from django import forms

from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext_lazy as _
from core.models import Address, Photo, Response, Message, ReportError,\
    ReportContent, ReportUser, Comment, ErrorType
class CommentForm( forms.ModelForm ):
    class Meta:
        model = Comment
        fields = ["text", "content" ]
        widgets = {
                   'content': HiddenInput()
                   }
class ReportUserForm( forms.ModelForm ):
    class Meta:
        model = ReportUser
        fields = [ "user", "comment", "reason" ]
        widgets = {
                   "user" : forms.HiddenInput()
                   }
        
class ReportContentForm( forms.ModelForm ):
    class Meta:
        model = ReportContent
        fields = [ "content", "comment", "reason" ]
        widgets = {
                   "content" : forms.HiddenInput()
                   }
class ReportErrorForm( forms.ModelForm ):
    class Meta:
        model = ReportError
        fields = [ "type", "comment" ]
        widgets = {
                   "type": forms.Select( choices = ErrorType.objects.all() )
                   }
       
class MessageForm( forms.Form ):
    title = forms.CharField( max_length = 255 )
    users = forms.CharField()
    text = forms.CharField( widget = forms.Textarea() )
    
    
class ResponseForm( forms.ModelForm ):
    class Meta:
        model = Response
        fields = [ "message", "text" ]
        widgets = { "message" : forms.HiddenInput() }
class ProfilePhotoForm( forms.ModelForm ):
    class Meta:
        model = Photo
        fields = ["image"]
class AddressForm( forms.ModelForm ):
    class Meta:
        model = Address
        exclude = [ "user" ]
        

class RegisterForm( forms.Form ):
    username = forms.CharField( max_length = 32 )
    password = forms.CharField( 
                               max_length = 32, 
                               widget = forms.widgets.PasswordInput(),
                              
                               )
    repassword = forms.CharField( max_length = 32, widget = forms.widgets.PasswordInput() )
    first_name = forms.CharField( max_length = 255 )
    last_name = forms.CharField( max_length = 255 )
    email = forms.EmailField()
    captcha_id = forms.IntegerField( widget = forms.widgets.HiddenInput() )
    captcha = forms.CharField( max_length = 8 )