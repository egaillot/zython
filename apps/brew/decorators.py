#-*- encoding:utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from brew.models import Recipe

def recipe_author(f, redirect_url="/"):
    def wrap(request, *args, **kwargs):
    	recipe_id = kwargs.get('recipe_id')
    	try:
    		r = Recipe.objects.get(
    			pk=recipe_id,
    			user=request.user
    		)
    	except Recipe.DoesNotExist:
            return HttpResponseRedirect("/")
        return f(request, *args, **kwargs)
    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap