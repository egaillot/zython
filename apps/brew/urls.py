from django.conf.urls.defaults import *
from django.views.generic import ListView, CreateView
from brew.views import RecipeCreateView, RecipeDetailView, ingredient_form, remove_ingredient
from brew.forms import * #RecipeForm, RecipeMaltForm
from brew.models import *

urlpatterns = patterns('',
    url(r'^add/$', RecipeCreateView.as_view(), name='brew_recipe_add'),
    url(r'^(?P<pk>\d+)/$', RecipeDetailView.as_view(), name='brew_recipe_detail'),

    url(r'^(?P<recipe_id>\d+)/add/(?P<ingredient>\w+)/$', 
        ingredient_form, 
        {'response': "json"},
        name='brew_recipe_addingredient'
    ),

    url(r'^(?P<recipe_id>\d+)/remove/(?P<ingredient>\w+)/(?P<object_id>\d+)/$', 
        remove_ingredient,
        name='brew_recipe_removeingredient'
    ),

    url(r'^(?P<recipe_id>\d+)/edit/(?P<ingredient>\w+)/(?P<object_id>\d+)/$', 
        ingredient_form, 
        {'response': "html", "template_name": "brew/raw_%(ingredient)s_form.html"}, 
        name='brew_recipe_editingredient'
    ),

)
