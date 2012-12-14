from django.db import models
import random
class CaptchaManager(  models.Manager ):
 
    def get(self, *args, **kwargs):
        if len( kwargs) > 0 :
            return super( CaptchaManager, self ).get( *args, **kwargs )
        _list = super( CaptchaManager, self ).all()
        if len( _list ) == 0:
            return None
        return random.choice( _list )
        