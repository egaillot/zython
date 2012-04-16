from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import simplejson as json
from django.db.models import Q
from django import http
from django.conf import settings
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView
from django.views.generic.edit import FormView, UpdateView

from brew.models import *
from brew.forms import *
from brew.decorators import recipe_author

from units.views import UnitViewFormMixin
import djnext 

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



"""
R E C I P E
-----------
"""

class RecipeListView(ListView):
    def get_queryset(self):
        self.user = None
        if self.request.user.is_active:
            qs = Recipe.objects.select_related(depth=3).filter(
                Q(private=False) | Q(user=self.request.user)
            )
        else:
            qs = Recipe.objects.filter(private=False)
        if self.kwargs.get("username"):
            user = get_object_or_404(User, username=self.kwargs.get("username"))
            self.user = user
            qs = qs.filter(user=user)
        return qs

    def get_context_data(self, **kwargs):
        context = super(RecipeListView, self).get_context_data(**kwargs)
        context['user_recipe'] = self.user
        return context


class RecipePreferenceView(UnitViewFormMixin, UpdateView):
    form_class = RecipePreferencesForm
    model = Recipe
    success_url = '.'
    template_name_suffix = '_preferences'
    pk_url_kwarg = 'recipe_id'

    @method_decorator(login_required)
    @method_decorator(recipe_author)
    def dispatch(self, *args, **kwargs):
        return super(RecipePreferenceView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RecipePreferenceView, self).get_context_data(**kwargs)
        context['page'] = "preferences"
        return context


class RecipeCreateView(UnitViewFormMixin, CreateView):
    form_class = RecipeForm
    model = Recipe
    success_url = '/brew/%(id)d/'
    
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
        for key, model in SLUG_MODELROOT.iteritems():
            context['%s_list' % key] = model.objects.all()
            context['%s_form' % key] = SLUG_MODELFORM[key](request=self.request)
        context['counter'] = 1
        context['page'] = "recipe"
        return context



"""
I N G R E D I E N T S
---------------------
"""

class IngredientFormView(FormView):
    def set_env(self):
        ingredient = self.kwargs.get("ingredient")
        recipe_id = self.kwargs.get("recipe_id")
        object_id = self.kwargs.get("object_id")
        self.recipe = get_object_or_404(Recipe, pk=recipe_id)
        self.model_class = SLUG_MODEL[ingredient]
        self.form_class = SLUG_MODELFORM[ingredient]
        self.instance = self.model_class(recipe=self.recipe)
        self.response_type = self.kwargs.get('response', "html")
        if object_id:
            self.instance = get_object_or_404(self.model_class, pk=object_id, recipe=self.recipe)
        self.template_name = self.kwargs.get("template_name") % {'ingredient': ingredient}
        self.context = {
            'recipe': self.recipe,
            'instance': self.instance,
            'ingredient': ingredient
        }

    def get(self, *args, **kwargs):
        self.set_env()
        self.context["form"] = self.form_class(instance=self.instance, request=self.request)
        if self.response_type == "json":
            return http.HttpResponseRedirect(self.recipe.get_absolute_url())
        return self.render_template()
        
    def post(self, request, *args, **kwargs):
        self.set_env()
        form = self.form_class(data=request.POST, instance=self.instance, request=self.request)
        out = {'valid': 0}
        status_code = 200
        if form.is_valid():
            form.save()
            out['valid'] = 1
            status_code = 202
        else:
            out['errors'] = ["%s: %s" % (k,v) for k,v  in form.errors.iteritems()]
        if self.response_type == "json":
            return http.HttpResponse(json.dumps(out), mimetype="application/json")
        self.context['form'] = form
        response = self.render_template()
        response.status_code = status_code
        return response

    def render_template(self):
        return render_to_response(self.template_name, self.context, 
            context_instance=RequestContext(self.request)
        )



"""
M A S H
-------
"""

class MashCreateView(CreateView):
    form_class = MashStepForm
    model = MashStep

    def get_form_kwargs(self):
        kwargs = super(MashCreateView, self).get_form_kwargs()
        recipe = get_object_or_404(Recipe, pk=self.kwargs['recipe_id'])
        ordering = recipe.mashstep_set.all().count() + 1
        kwargs["instance"] = MashStep(recipe=recipe, ordering=ordering)
        initial = kwargs.get("initial", None) or {}

        if not recipe.mashstep_set.all().count():
            initial["water_added"] = "%.2f" % recipe.water_initial_mash()
            initial["name"] = "Mash in"
            initial["step_type"] = "temperature"
            initial["temperature"] = "66.0"
            initial["step_time"] = "60"
            initial["rise_time"] = "10"
        else:
            initial["step_type"] = "temperature"
            initial["water_added"] = "0"
            initial["name"] = "Mash step"
            initial["rise_time"] = "10"
        kwargs["initial"] = initial
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        form.save()
        resp = http.HttpResponse()
        resp.status_code = 202
        return resp



# --------------------
# -- View functions --
# --------------------

@login_required
@recipe_author
def ingredient_form(request, recipe_id, ingredient, object_id=None, response="json", template_name="none.html"):
    model_class = SLUG_MODEL[ingredient]
    form_class = SLUG_MODELFORM[ingredient]
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if object_id:
        instance = get_object_or_404(model_class, pk=object_id, recipe=recipe)
    else:
        instance = model_class(recipe=recipe)
    out = {}
    if request.method == "POST":
        form = form_class(data=request.POST, instance=instance, request=request)
        if form.is_valid():
            form.save()
            out['valid'] = 1
            if response == "raw":
                resp = http.HttpResponse('')
                resp.status_code = 202
                return resp
            if response == "html":
                return http.HttpResponseRedirect(recipe.get_absolute_url())
        else:
            out['valid'] = 0
            out['errors'] = ["%s: %s" % (k,v) for k,v  in form.errors.iteritems()]
        if response == "json":
            json_response = json.dumps(out)
            return http.HttpResponse(json_response, mimetype="application/json")
    else:
        form = form_class(instance=instance, request=request)
    if response == "json":
        return http.HttpResponseRedirect(recipe.get_absolute_url())
    context = {
        'form': form,
        'recipe': recipe,
        'instance': instance,
        'ingredient': ingredient
    }
    template_name = template_name % {'ingredient': ingredient}
    return render_to_response(template_name, context, 
        context_instance=RequestContext(request)
    )

@login_required
@recipe_author
def remove_ingredient(request, recipe_id, ingredient, object_id):
    model_class = SLUG_MODEL[ingredient]
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    ingredient = get_object_or_404(model_class, pk=object_id, recipe=recipe)
    ingredient.delete()
    next = djnext.ref_get_post(request, recipe.get_absolute_url())
    return http.HttpResponseRedirect(next)

@login_required
@recipe_author
def mash_order(request, recipe_id, object_id, direction):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    mash = get_object_or_404(MashStep, pk=object_id, recipe=recipe)
    mash.set_order(direction)
    return http.HttpResponseRedirect(recipe.get_absolute_url())


@login_required
@recipe_author
def mash_delete(request, recipe_id, object_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    mash = get_object_or_404(MashStep, pk=object_id, recipe=recipe)
    mash.delete()
    return http.HttpResponseRedirect(recipe.get_absolute_url())

