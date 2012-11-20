from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import simplejson as json
from django.db.models import Q
from django import http
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.views.generic.edit import FormView, UpdateView
from django.core.urlresolvers import reverse

from brew.models import *
from brew.forms import *
from brew.helpers import import_beer_xml
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


class RecipeAuthorMixin(object):
    '''
    Mixin object to authorise recipe author
    acessing views (deletion, updates...)
    '''
    model = Recipe
    pk_url_kwarg = 'recipe_id'

    @method_decorator(login_required)
    @method_decorator(recipe_author)
    def dispatch(self, *args, **kwargs):
        return super(RecipeAuthorMixin, self).dispatch(*args, **kwargs)


class RecipeListView(ListView):
    def search_form(self, qs):
        if self.request.GET:
            search_form = RecipeSearchForm(self.request.GET)
            if search_form.is_valid():
                qs = search_form.search(qs)
        else:
            search_form = RecipeSearchForm()
        self.search_form = search_form
        return qs

    def get_queryset(self):
        self.user = None
        queryset = Recipe.objects.select_related('user', 'style')
        if self.request.user.is_active:
            qs = queryset.filter(
                Q(private=False) | Q(user=self.request.user)
            )
        else:
            qs = queryset.filter(private=False)
        if self.kwargs.get("username"):
            user = get_object_or_404(User, username=self.kwargs.get("username"))
            self.user = user
            qs = qs.filter(user=user)
        else:
            qs = self.search_form(qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super(RecipeListView, self).get_context_data(**kwargs)
        context['user_recipe'] = self.user
        if not self.user:
            context['search_form'] = getattr(self, 'search_form')
        return context


class RecipeCreateView(UnitViewFormMixin, CreateView):
    form_class = RecipeForm
    model = Recipe
    success_url = '/recipe/%(id)d/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RecipeCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        self.object = obj
        return http.HttpResponseRedirect(self.get_success_url())

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(CreateView, self).get_initial()
        recipes = self.request.user.recipe_set.all().order_by('-created')
        if recipes.count() > 0:
            recipe = recipes[0]
            initial['boiler_tun_deadspace'] = recipe.boiler_tun_deadspace
            initial['mash_tun_deadspace'] = recipe.mash_tun_deadspace
            initial['evaporation_rate'] = recipe.evaporation_rate
        return initial


class RecipeImportView(FormView):
    form_class = RecipeImportForm
    template_name = "brew/recipe_import_form.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RecipeImportView, self).dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        xml_data = self.request.FILES.get('beer_file').read()
        recipes = import_beer_xml(xml_data, self.request.user)
        return http.HttpResponseRedirect(reverse(
            'brew_recipe_user',
            args=[self.request.user.username]
        ))


class RecipeDetailView(DetailView):
    model = Recipe

    def dispatch(self, *args, **kwargs):
        response = super(RecipeDetailView, self).dispatch(*args, **kwargs)
        if self.object.private and self.request.user != self.object.user:
            raise http.Http404()
        return response

    def render_to_response(self, context, **kwargs):
        if self.template_name_suffix == "_text":
            kwargs["content_type"] = "text/plain; charset=utf-8"
        return super(RecipeDetailView, self).render_to_response(
            context, **kwargs
        )

    def get_template_names(self):
        if self.template_name_suffix == "_text":
            return "brew/recipe_detail.txt"
        return super(RecipeDetailView, self).get_template_names()

    def get_context_data(self, **kwargs):
        context = super(RecipeDetailView, self).get_context_data(**kwargs)
        if self.request.user.is_active:
            for key, model in SLUG_MODELROOT.iteritems():
                context['%s_list' % key] = model.objects.all()
                context['%s_form' % key] = SLUG_MODELFORM[key](request=self.request)
        context['counter'] = 1
        context['page'] = "recipe"
        context['controls'] = self.object.all_controls()
        if "print" in self.template_name_suffix:
            context['can_edit'] = False
            context['version'] = "print"
        elif "comment" in self.template_name_suffix:
            context['page'] = "comments"
        else:
            context['version'] = "detail"
        context['can_edit'] = self.request.user == self.object.user
        return context


class RecipeDeleteView(RecipeAuthorMixin, DeleteView):
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super(RecipeDeleteView, self).get_context_data(**kwargs)
        context['page'] = "delete"
        context['can_edit'] = self.request.user == self.object.user
        return context


class RecipeUpdateView(RecipeAuthorMixin, UnitViewFormMixin, UpdateView):
    form_class = RecipeForm
    success_url = '/recipe/%(id)d/'


class StyleListView(ListView):
    model = BeerStyle


class StyleDetailView(DetailView):
    model = BeerStyle

    def get_context_data(self, **kwargs):
        context = super(StyleDetailView, self).get_context_data(**kwargs)
        queryset = Recipe.objects.filter(style=self.object).select_related('user', 'style')
        if self.request.user.is_active:
            qs = queryset.filter(
                Q(private=False) | Q(user=self.request.user)
            )
        else:
            qs = queryset.filter(private=False)
        context['related_recipes'] = qs
        context['same_category_styles'] = BeerStyle.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)
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
            out['errors'] = ["%s: %s" % (k, v) for k, v in form.errors.iteritems()]
        if self.response_type == "json":
            return http.HttpResponse(json.dumps(out), mimetype="application/json")
        self.context['form'] = form
        response = self.render_template()
        response.status_code = status_code
        return response

    def render_template(self):
        return render_to_response(
            self.template_name, self.context,
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


class MashUpdateView(UnitViewFormMixin, UpdateView):
    form_class = MashStepForm
    model = MashStep
    pk_url_kwarg = 'object_id'
    template_name_suffix = "_form"

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
            out['errors'] = ["%s: %s" % (k, v) for k, v in form.errors.iteritems()]
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
    return render_to_response(
        template_name, context,
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
