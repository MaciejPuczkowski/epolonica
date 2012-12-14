from django import forms
from django.utils.translation import ugettext_lazy as _
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