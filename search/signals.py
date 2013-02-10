# -*- coding: utf-8 -*-
from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save


def search_register( sender , instance , created , **kwargs ):
    pass
