from django.db import models
import random
import core.models



class ContentManager( models.Manager ):
    model_class = None
    comment_form = None
    def setCommentForm(self, form ):
        self.comment_form = form
    
    def setModel(self, model ):
        self.model_class = model
    def get_query_set(self):
        queryset = super( ContentManager, self ).get_query_set()
        for query in queryset:
            query.rank = core.models.Vote.objects.filter( content = query, promotion = True ).count()
            if self.comment_form is not None:
                query.comment_form = self.comment_form( initial = { "content" : query } )
                
        return queryset
    def get(self, *args, **kwargs):
        content = super( ContentManager, self ).get( *args, **kwargs )
        content.rank = core.models.Vote.objects.filter( content = content, promotion = True ).count() 
        return content
    def getForUser(self, user ):
        raise NotImplemented()
    def promoted(self, user = None ):
        return self.get_query_set()

class VoteManager( models.Manager ):
    def get(self, *args, **kwargs):
        try:
            return models.Manager.get(self, *args, **kwargs)
        except core.models.Vote.DoesNotExist as e:
            return None
        
    def vote(self, id, user ):
        content = core.models.Content.objects.get( id = id )
        vote = core.models.Vote.objects.get( content = content, votingUser = user )
        if vote is  None:
            vote = core.models.Vote.objects.create( votingUser = user, promotion = False, content = content )
        vote.promotion = not vote.promotion
        vote.save()
        return vote.promotion
    def getRank(self, id ):
        content = core.models.Content.objects.get( id = id )
        return core.models.Vote.objects.filter( content = content ).count()
        
        
class MessageManager( models.Manager ):
    pass

class CaptchaManager(  models.Manager ):
 
    def get(self, *args, **kwargs):
        if len( kwargs) > 0 :
            return super( CaptchaManager, self ).get( *args, **kwargs )
        _list = super( CaptchaManager, self ).all()
        if len( _list ) == 0:
            return None
        return random.choice( _list )
        