from django.conf.urls.defaults import *
from django.views.generic import ListView, CreateView
from brew.views import RecipeCreateView, RecipeDetailView, add_ingredient, remove_ingredient
from brew.forms import * #RecipeForm, RecipeMaltForm
from brew.models import *

urlpatterns = patterns('',
    url(r'^add/$', RecipeCreateView.as_view(), name='brew_recipe_add'),
    url(r'^(?P<pk>\d+)/$', RecipeDetailView.as_view(), name='brew_recipe_detail'),

    url(r'^(?P<recipe_id>\d+)/add/malt/$', 
        add_ingredient, 
        {'model_class':RecipeMalt, 'form_class':RecipeMaltForm},
        name='brew_recipe_addmalt'
    ),
    
    url(r'^(?P<recipe_id>\d+)/add/hop/$', 
        add_ingredient, 
        {'model_class':RecipeHop, 'form_class':RecipeHopForm},
        name='brew_recipe_addhop'
    ),

    url(r'^(?P<recipe_id>\d+)/add/misc/$', 
        add_ingredient, 
        {'model_class':RecipeMisc, 'form_class':RecipeMiscForm},
        name='brew_recipe_addmisc'
    ),


    url(r'^(?P<recipe_id>\d+)/remove/malt/(?P<object_id>\d+)/$', 
        remove_ingredient, 
        {'model_class':RecipeMalt,},
        name='brew_recipe_removemalt'
    ),

    url(r'^(?P<recipe_id>\d+)/remove/hop/(?P<object_id>\d+)/$', 
        remove_ingredient, 
        {'model_class':RecipeHop,},
        name='brew_recipe_removehop'
    ),

    url(r'^(?P<recipe_id>\d+)/remove/misc/(?P<object_id>\d+)/$', 
        remove_ingredient, 
        {'model_class':RecipeMisc,},
        name='brew_recipe_removemisc'
    ),
)
