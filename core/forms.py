# -*- coding: utf-8 -*-
from django import forms
from models import Comment, ReportContent, ReportUser, Message, Response
from django.forms.widgets import HiddenInput
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
        field = [ "user", "comment", "reason" ]
        
        
class ReportContentForm( forms.ModelForm ):
    class Meta:
        model = ReportContent
        field = [ "content", "comment", "reason" ]
class ReportErrorForm( forms.ModelForm ):
    class Meta:
        model = ReportContent
        field = [ "type", "comment" ]
       
class MessageForm( forms.ModelForm ):
    class Meta:
        model = Message
        field = [ "title", "users", "text" ]
class ResponseForm( forms.ModelForm ):
    class Meta:
        model = Response
        field = [ "message", "text" ]