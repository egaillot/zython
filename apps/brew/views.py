from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import simplejson as json
from django import http
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView

from brew.models import Recipe, Hop, Malt, Misc, Yeast, RecipeMalt
from brew.forms import *
from brew.decorators import recipe_author

import djnext 


class RecipeListView(ListView):
    def get_queryset(self):
        return Recipe.objects.all()


class RecipeCreateView(CreateView):
    form_class = RecipeForm
    model = Recipe
    success_url = '/brew/%(id)d/'

    def get_form_kwargs(self):
        kwargs = super(RecipeCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RecipeCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        self.object = obj      
        return http.HttpResponseRedirect(self.get_success_url())


class RecipeDetailView(DetailView):
    model = Recipe

    def get_context_data(self, **kwargs):
        context = super(RecipeDetailView, self).get_context_data(**kwargs)
        context['malt_list'] = Malt.objects.all()
        context['hop_list'] = Hop.objects.all()
        context['misc_list'] = Misc.objects.all()
        context['yeast_list'] = Yeast.objects.all()
        context['malt_form'] = RecipeMaltForm(request=self.request)
        context['hop_form'] = RecipeHopForm(request=self.request)
        context['misc_form'] = RecipeMiscForm(request=self.request)
        context['counter'] = 1
        return context

# --------------------
# -- View functions --
# --------------------

@login_required
@recipe_author
def add_ingredient(request, recipe_id, model_class, form_class):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    instance = model_class(recipe=recipe)
    response = {}
    if request.method == "POST":
        form = form_class(data=request.POST, instance=instance, request=request)
        if form.is_valid():
            form.save()
            response['valid'] = 1
        else:
            response['valid'] = 0
            response['errors'] = ["%s: %s" % (k,v) for k,v  in form.errors.iteritems()]
        json_response = json.dumps(response)
        return http.HttpResponse(json_response, mimetype="application/json")
    return http.HttpResponseRedirect(recipe.get_absolute_url())

@login_required
@recipe_author
def remove_ingredient(request, recipe_id, object_id, model_class):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    ingredient = get_object_or_404(model_class, pk=object_id, recipe=recipe)
    ingredient.delete()
    next = djnext.ref_get_post(request, recipe.get_absolute_url())
    return http.HttpResponseRedirect(next)

