from django.db import models
class ContentManager( models.Manager ):
    pass

class VoteManager( models.Manager ):
    pass
class ReportManager( models.Manager ):
    pass
class CommentManager( models.Manager ):
    pass

class EventManager( models.Manager ):
    pass
class MessageManager( models.Manager ):
    pass