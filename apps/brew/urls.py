from django.conf.urls import patterns, url
from brew.views import *
from brew.forms import * 
from brew.models import *

urlpatterns = patterns('',
    url(r'^add/$', RecipeCreateView.as_view(), name='brew_recipe_add'),
    url(r'^import/$', RecipeImportView.as_view(), name='brew_recipe_import'),

    url(r'^user/(?P<username>\w+)/$', 
        RecipeListView.as_view(),
        name='brew_recipe_user'
    ),

    url(r'^(?P<pk>\d+)/$', RecipeDetailView.as_view(), name='brew_recipe_detail'),
    url(r'^(?P<pk>\d+)/comments/$', RecipeDetailView.as_view(page="comments"), name='brew_recipe_comments'),
    url(r'^(?P<pk>\d+)/changes/$', RecipeDetailView.as_view(page="changes"), name='brew_recipe_changes'),
    url(r'^(?P<pk>\d+)/permissions/$', RecipeDetailView.as_view(page="permissions"), name='brew_recipe_permissions'),
    url(r'^(?P<recipe_id>\d+)/permissions/set/$', set_user_perm, name='brew_recipe_setperms'),
    url(r'^(?P<pk>\d+)/print/$', RecipeDetailView.as_view(page="print"), name='brew_recipe_print'),
    url(r'^(?P<pk>\d+)/text/$', RecipeDetailView.as_view(page="text"), name='brew_recipe_text'),
    url(r'^(?P<recipe_id>\d+)/confirm-delete/$', RecipeDeleteView.as_view(), name='brew_recipe_delete'),
    url(r'^(?P<recipe_id>\d+)/edit/$', RecipeUpdateView.as_view(), name='brew_recipe_edit'),
    url(r'^(?P<recipe_id>\d+)/clone/$', RecipeCloneView.as_view(), name='brew_recipe_clone'),

    url(r'^(?P<recipe_id>\d+)/add/(?P<ingredient>\w+)/$', 
        ingredient_form, 
        {'response': "raw", "template_name": "brew/raw_%(ingredient)s_form.html"},
        name='brew_recipe_addingredient'
    ),

    url(r'^(?P<recipe_id>\d+)/remove/(?P<ingredient>\w+)/(?P<object_id>\d+)/$', 
        remove_ingredient,
        name='brew_recipe_removeingredient'
    ),

    url(r'^(?P<recipe_id>\d+)/edit/(?P<ingredient>\w+)/(?P<object_id>\d+)/$', 
        ingredient_form, 
        {'response': "raw", "template_name": "brew/raw_%(ingredient)s_form.html"}, 
        name='brew_recipe_editingredient'
    ),

    url(r'^(?P<recipe_id>\d+)/mash/add/$', 
        MashCreateView.as_view(), 
        name="brew_mash_add"
    ),

    url(r'^(?P<recipe_id>\d+)/mash/(?P<object_id>\d+)/edit/$', 
        MashUpdateView.as_view(),  
        name="brew_mash_edit"
    ),

    url(r'^(?P<recipe_id>\d+)/mash/(?P<object_id>\d+)/order/(?P<direction>\w+)/$', 
        mash_order, 
        name="brew_mash_order"
    ),
    
    url(r'^(?P<recipe_id>\d+)/mash/(?P<object_id>\d+)/delete/$', 
        mash_delete, 
        name="brew_mash_delete"
    ),

    url(r'^style/$', 
        StyleListView.as_view(),
        name="brew_style_list"
    ),

    url(r'^style/(?P<pk>\d+)/$', 
        StyleDetailView.as_view(),
        name="brew_style_detail"
    ),

)
