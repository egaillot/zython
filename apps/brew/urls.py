from django.conf.urls import patterns, url
from .views import *
from .forms import *
from .models import *

urlpatterns = patterns(
    '',

    url(r'^add/$', RecipeCreateView.as_view(),
        name='brew_recipe_add'),

    url(r'^import/$', RecipeImportView.as_view(),
        name='brew_recipe_import'),

    url(r'^user/(?P<username>\w+)/$',
        RecipeListView.as_view(),
        name='brew_recipe_user'),

    url(r'^user/$',
        UserListView.as_view(),
        name='brew_recipe_users'),

    url(r'^by-style/$',
        StyleRecipesView.as_view(),
        name="brew_recipe_styles"),

    url(r'^by-style/(?P<slug>[\w-]+)-(?P<pk>\d+)/$',
        StyleRecipeView.as_view(),
        name="brew_recipe_style"),

    url(r'^(?P<pk>\d+)/$',
        RecipeDetailView.as_view(),
        name='brew_recipe_detail'),

    url(r'^(?P<pk>\d+)/comments/$',
        RecipeDetailView.as_view(page="comments"),
        name='brew_recipe_comments'),

    url(r'^(?P<pk>\d+)/permissions/$',
        RecipeDetailView.as_view(page="permissions"),
        name='brew_recipe_permissions'),

    url(r'^(?P<recipe_id>\d+)/permissions/set/$',
        set_user_perm,
        name='brew_recipe_setperms'),

    url(r'^(?P<pk>\d+)/print/$',
        RecipeDetailView.as_view(page="print"),
        name='brew_recipe_print'),

    url(r'^(?P<pk>\d+)/text/$',
        RecipeDetailView.as_view(page="text"),
        name='brew_recipe_text'),

    url(r'^(?P<recipe_id>\d+)/confirm-delete/$',
        RecipeDeleteView.as_view(),
        name='brew_recipe_delete'),

    url(r'^(?P<recipe_id>\d+)/destock/$',
        RecipeDestockView.as_view(),
        name='brew_recipe_destock'),

    url(r'^(?P<recipe_id>\d+)/edit/$',
        RecipeUpdateView.as_view(),
        name='brew_recipe_edit'),

    url(r'^(?P<recipe_id>\d+)/clone/$',
        RecipeCloneView.as_view(),
        name='brew_recipe_clone'),

    url(r'^(?P<recipe_id>\d+)/add/(?P<ingredient>\w+)/$',
        IngredientCreateView.as_view(),
        name='brew_recipe_addingredient'),

    url(r'^(?P<recipe_id>\d+)/remove/(?P<ingredient>\w+)/(?P<object_id>\d+)/$',
        remove_ingredient,
        name='brew_recipe_removeingredient'),

    url(r'^(?P<recipe_id>\d+)/edit/(?P<ingredient>\w+)/(?P<object_id>\d+)/$',
        IngredientUpdateView.as_view(),
        name='brew_recipe_editingredient'),

    url(r'^(?P<recipe_id>\d+)/mash/add/$',
        MashCreateView.as_view(),
        name="brew_mash_add"),

    url(r'^(?P<recipe_id>\d+)/mash/(?P<object_id>\d+)/edit/$',
        MashUpdateView.as_view(),
        name="brew_mash_edit"),

    url(r'^(?P<recipe_id>\d+)/mash/(?P<object_id>\d+)/delete/$',
        mash_delete,
        name="brew_mash_delete"),

    url(r'^guide/style/$',
        StyleListView.as_view(),
        name="brew_style_list"),

    url(r'^guide/style/(?P<pk>\d+)/$',
        StyleDetailView.as_view(),
        name="brew_style_detail")
)
