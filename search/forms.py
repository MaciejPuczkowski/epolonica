# -*- coding: utf-8 -*-
from django import forms

class SearchLine( forms.Form ):
    line = forms.CharField()