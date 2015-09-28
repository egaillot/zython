import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django import http
from django.contrib import messages
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.views.generic.edit import FormView, UpdateView
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from braces.views import LoginRequiredMixin
from brew.models import *
from brew.forms import *
from brew.helpers import import_beer_xml
from brew.decorators import recipe_author
from stocks.choices import INGREDIENTS_DICT
from units.views import UnitViewFormMixin
import djnext
from guardian.shortcuts import get_users_with_perms, assign, get_perms_for_model, remove_perm

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


class RecipeAuthorMixin(LoginRequiredMixin):
    '''
    Mixin object to authorise recipe author
    acessing views (deletion, updates...)
    '''
    model = Recipe
    pk_url_kwarg = 'recipe_id'

    @method_decorator(recipe_author)
    def dispatch(self, *args, **kwargs):
        return super(RecipeAuthorMixin, self).dispatch(*args, **kwargs)


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


class RecipeListView(ListView):
    user = None

    def search_form(self, qs):
        if self.kwargs.get("username"):
            # Display User page
            user = get_object_or_404(User, username=self.kwargs.get("username"))
            self.user = user
            qs = qs.filter(user=user)
        else:
            if self.request.GET:
                search_form = RecipeSearchForm(self.request.GET)
                if search_form.is_valid():
                    qs = search_form.search(qs)
            else:
                search_form = RecipeSearchForm()
            self.search_form = search_form
        return qs

    def get_queryset(self):
        qs = Recipe.objects.for_user(self.request.user).select_related('user', 'style')
        return self.search_form(qs)

    def get_context_data(self, **kwargs):
        context = super(RecipeListView, self).get_context_data(**kwargs)
        context['user_recipe'] = self.user
        if self.user is None:
            context['search_form'] = getattr(self, 'search_form')
        return context


class UserListView(ListView):
    model = User
    template_name = "brew/user_list.html"

    def get_queryset(self):
        qs = super(UserListView, self).get_queryset()
        return qs.filter(recipe__private=False).distinct().order_by("-date_joined")


class StyleRecipesView(ListView):
    model = BeerStyle
    template_name = "brew/style_list.html"

    def get_queryset(self):
        qs = super(StyleRecipesView, self).get_queryset()
        return qs.filter(recipe__private=False).distinct()


class StyleRecipeView(RecipeListView):
    template_name = "brew/style_recipe_list.html"

    def get_context_data(self, **kwargs):
        context = super(StyleRecipeView, self).get_context_data(**kwargs)
        context["style"] = get_object_or_404(BeerStyle.objects, pk=self.kwargs["pk"])
        return context

    def get_queryset(self):
        qs = super(StyleRecipeView, self).get_queryset().filter(style__pk=self.kwargs["pk"])
        return qs


class RecipeCreateView(LoginRequiredMixin, UnitViewFormMixin, CreateView):
    form_class = RecipeForm
    model = Recipe
    success_url = '/recipe/%(id)d/'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        self.object = obj
        return http.HttpResponseRedirect(self.get_success_url())

    def get_initial(self):
        """Get the previous data used."""
        initial = super(CreateView, self).get_initial()
        recipes = self.request.user.recipe_set.all().order_by('-created')
        if recipes.count() > 0:
            recipe = recipes[0]
            initial['boiler_tun_deadspace'] = recipe.boiler_tun_deadspace
            initial['mash_tun_deadspace'] = recipe.mash_tun_deadspace
            initial['evaporation_rate'] = recipe.evaporation_rate
        return initial


class RecipeImportView(LoginRequiredMixin, FormView):
    form_class = RecipeImportForm
    template_name = "brew/recipe_import_form.html"

    def post(self, *args, **kwargs):
        xml_data = self.request.FILES.get('beer_file').read()
        recipes = import_beer_xml(xml_data, self.request.user)
        return http.HttpResponseRedirect(reverse(
            'brew_recipe_user',
            args=[self.request.user.username]
        ))


class RecipeDetailView(RecipeViewableMixin, DetailView):
    model = Recipe
    pk_url_kwarg = 'pk'
    page = "detail"

    def dispatch(self, *args, **kwargs):
        response = super(RecipeDetailView, self).dispatch(*args, **kwargs)
        if "permissions" in self.template_name_suffix and self.request.user != self.object.user:
            return http.HttpResponseRedirect(self.object.get_absolute_url())
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
        self.template_name_suffix = "_%s" % self.page
        can_edit = self.request.user == self.object.user or self.request.user.has_perm('change_recipe', self.object)
        if self.page == "print":
            can_edit = False
        elif self.page == "permissions":
            context['user_perms'] = get_users_with_perms(self.object)
            context['object_perms'] = get_perms_for_model(self.object)
        if can_edit and self.page == 'detail':
            context['controls'] = self.object.all_controls()
            if 'open_modal' in self.request.session.iterkeys():
                context['open_modal'] = self.request.session['open_modal']
                del self.request.session['open_modal']

        context.update({
            'page': self.page,
            'can_edit': can_edit
        })
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


class RecipeCloneView(LoginRequiredMixin, RecipeViewableMixin, DetailView):
    template_name = "brew/recipe_clone.html"

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        new_recipe = self.object.clone_to_user(self.request.user)
        response = http.HttpResponse()
        response['Location'] = new_recipe.get_absolute_url()
        return response


class RecipeDestockView(RecipeAuthorMixin, DetailView):
    template_name = "brew/recipe_destock.html"

    def previsionnal_stocks_ingredient(self, ingredient_slug):
        model_class = SLUG_MODELROOT[ingredient_slug]

        available_stocks = model_class.objects.filter(
            **{"recipe%s__recipe" % ingredient_slug: self.object}
        ).stocked(user=self.request.user).distinct()

        recipeingredients = getattr(self.object, "get_stocked_recipe%ss" % ingredient_slug)()
        datas = []

        for stocked_ingredient in available_stocks:
            data = {
                "object": stocked_ingredient,
                "initial_amount": stocked_ingredient.stock_amount,
                "remaining_amount": stocked_ingredient.stock_amount,
                "errors": False,
                'recipe_ingredients': []
            }
            for ri in recipeingredients.filter(**{ingredient_slug: stocked_ingredient}):
                data['recipe_ingredients'].append(ri)
                data['remaining_amount'] -= ri.amount
            if data['remaining_amount'] < 0:
                data['remaining_amount'] = 0
                data["errors"] = True
            datas.append(data)
        return datas

    def get_context_data(self, **kwargs):
        context = super(RecipeDestockView, self).get_context_data(**kwargs)
        self.object = self.get_object()
        # malts = self.object.get_stocked_recipemalts()
        # hops = self.object.get_stocked_recipehops()
        # yeasts = self.object.get_stocked_recipeyeast()
        # context["malts"] = malts
        # context["hops"] = hops
        # context["yeasts"] = yeasts
        ingredients = {}
        for k in INGREDIENTS_DICT.iterkeys():
            ingredients["%ss" % k] = self.previsionnal_stocks_ingredient(k)
        context["ingredients"] = ingredients
        return context


# --------------------
# -- View functions --
# --------------------

@login_required
@recipe_author
def ingredient_form(request, recipe_id, ingredient, object_id=None, response="json", template_name="none.html"):
    response = "raw"
    model_class = SLUG_MODEL[ingredient]
    form_class = SLUG_MODELFORM[ingredient]
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    adding = object_id is None
    if object_id:
        instance = get_object_or_404(model_class, pk=object_id, recipe=recipe)
    else:
        instance = model_class(recipe=recipe)
    out = {}
    if request.method == "POST":
        form = form_class(data=request.POST, instance=instance, request=request)
        if form.is_valid():
            saved_instance = form.save()
            out['valid'] = 1
            if adding:
                request.session['open_modal'] = "%s_%s" % (ingredient, saved_instance.id)

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


@login_required
@recipe_author
def set_user_perm(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    username = request.POST.get('username')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, _("User %s does not exist" % username))
    else:
        raw_perms = request.POST.get('perms')
        perms = raw_perms.split("|")
        init_perms = ['change_recipe', 'view_recipe']
        for perm in init_perms:
            remove_perm(perm, user, recipe)
        for perm in perms:
            if perm:
                assign(perm, user, recipe)
        if raw_perms:
            messages.success(request, _("Permissions added for user %s" % username))
        else:
            messages.success(request, _("Permissions removed for user %s" % username))
    return http.HttpResponseRedirect(reverse('brew_recipe_permissions', args=[recipe_id]))
