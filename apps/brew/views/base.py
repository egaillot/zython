from django import http
from django.utils.decorators import method_decorator
from braces.views import LoginRequiredMixin

from ..decorators import recipe_author
from ..models import Recipe, RecipeHop, RecipeMalt, RecipeMisc, RecipeYeast, Malt, Misc, Hop, Yeast
from ..forms import RecipeMaltForm, RecipeHopForm, RecipeMiscForm, RecipeYeastForm

SLUG_MODEL = {
    'malt': RecipeMalt,
    'misc': RecipeMisc,
    'hop': RecipeHop,
    'yeast': RecipeYeast
}

SLUG_MODELROOT = {
    'malt': Malt,
    'misc': Misc,
    'hop': Hop,
    'yeast': Yeast
}

SLUG_MODELFORM = {
    'malt': RecipeMaltForm,
    'misc': RecipeMiscForm,
    'hop': RecipeHopForm,
    'yeast': RecipeYeastForm
}


class RecipeAuthorMixin(LoginRequiredMixin):
    '''
    Mixin object to authorise recipe author
    acessing views (deletion, updates...)
    '''
    model = Recipe
    pk_url_kwarg = 'recipe_id'

    @method_decorator(recipe_author)
    def dispatch(self, request, recipe, *args, **kwargs):
        self.recipe = recipe
        return super(RecipeAuthorMixin, self).dispatch(request, *args, **kwargs)


class RecipeViewableMixin(object):
    """
    The recipe can be viewed by the current user
    """
    model = Recipe
    pk_url_kwarg = 'recipe_id'

    def dispatch(self, *args, **kwargs):
        response = super(RecipeViewableMixin, self).dispatch(*args, **kwargs)
        if not self.object.can_be_viewed_by_user(self.request.user):
            raise http.Http404()
        return response
