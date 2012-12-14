# -*- coding: utf-8 -*-
from django.views.generic.edit import FormView
from registration.forms import RegisterForm
from registration.models import Captcha, Activation
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponseNotFound
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from ePolonica.settings import EMAIL_HOST_USER
from django.views.generic.base import TemplateView, View

activation_timeout = timedelta( days = 7 )

class RegistrationView( FormView ):
    success_url = "/"
    def invalid(self, form, request, message = None ):
        captcha = Captcha.objects.get( id = int( form.data["captcha_id" ] ) )
        data = { "form" : form.as_p(), 'captcha': captcha.asHtml() }
        data.update( csrf( request ) )
        return render_to_response("registration/form.html", data )
    def get(self, request, *args, **kwargs):
        captcha = Captcha.objects.get()
        form = RegisterForm( initial = {"captcha_id" : captcha.id } )
        data = { "form" : form.as_p(), 'captcha': captcha.asHtml() }
        data.update( csrf( request ) )
        return render_to_response("registration/form.html", data )
    def post(self, request, *args, **kwargs):
        form = RegisterForm( request.POST )
        if form.is_valid():
            data = form.cleaned_data
            captcha = Captcha.objects.get( id = int( data["captcha_id" ] ) )
            if captcha.code != data["captcha"] or data["password"] != data["repassword"]:
                return self.invalid( form , request )
            if User.objects.filter( email = data["email"] ).count() > 0:
                return self.invalid( form , request )
            if User.objects.filter( username = data["username"] ).count() > 0:
                return self.invalid( form , request )
            del data["captcha"]
            del data["captcha_id"]
            del data["repassword"]
            data["is_active"] = False
            
            user = User( **data )
            user.save()
            code = "fake"
            Activation.objects.create( user = user, code = code, timeout = datetime.now() + activation_timeout )
            url = "registration/activate/" + user.username +"/" + code
            activation_message = """
                Thank you for registration in ePolonice.
                This is your activation url:\n %s
                        """ % url
            send_mail(
                      _("Activation"),
                      activation_message, 
                      EMAIL_HOST_USER,
                      [user.email], fail_silently=False
                      )
            return render_to_response("registration/registration_success.html", { "success_url": self.success_url })
        else:
            return self.invalid( form, request )
        
class ActivationView( View ):
    def dispatch(self, request, *args, **kwargs):
        try:
            code = kwargs["code"]
            username = kwargs["user"]
            user = User.objects.get( username = username )
            activs = Activation.objects.filter( user = user )
            ok_activs = activs.filter( timeout__gte = datetime.now() )
            for oka in ok_activs:
                if oka.code == code:
                    user.is_active = True
                    return render_to_response("registration/activation.html")
        except:
            pass
        finally:
            return HttpResponseNotFound()
                
    