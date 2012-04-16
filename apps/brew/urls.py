from django.conf.urls.defaults import *
from django.views.generic import ListView, CreateView
from brew.views import *
from brew.forms import * 
from brew.models import *

urlpatterns = patterns('',
    url(r'^add/$', RecipeCreateView.as_view(), name='brew_recipe_add'),

    url(r'^user/(?P<username>\w+)/$', 
        RecipeListView.as_view(),
        name='brew_recipe_user'
    ),

    url(r'^(?P<pk>\d+)/$', RecipeDetailView.as_view(), name='brew_recipe_detail'),
    url(r'^(?P<recipe_id>\d+)/preferences/$', RecipePreferenceView.as_view(), name='brew_recipe_preferences'),

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
        IngredientFormView.as_view(), 
        {'response': "raw", "template_name": "brew/raw_%(ingredient)s_form.html"}, 
        name='brew_recipe_editingredient'
    ),

    url(r'^(?P<recipe_id>\d+)/mash/add/$', 
        MashCreateView.as_view(), 
        name="brew_mash_add"
    ),

    url(r'^(?P<recipe_id>\d+)/mash/(?P<object_id>\d+)/order/(?P<direction>\w+)/$', 
        mash_order, 
        name="brew_mash_order"
    ),
    

    url(r'^(?P<recipe_id>\d+)/mash/(?P<object_id>\d+)/delete/$', 
        mash_delete, 
        name="brew_mash_delete"
    ),

    
)
