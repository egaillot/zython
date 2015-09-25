# -*- coding: utf-8 -*-
from django.views.generic import TemplateView,  ListView, CreateView, UpdateView, DeleteView
from django import http
from .models import StockHop, StockMalt, StockYeast
from .forms import StockMaltForm, StockHopForm, StockYeastForm
from .choices import INGREDIENT_MALT, INGREDIENT_HOP, INGREDIENT_YEAST, INGREDIENTS_DICT
from public.utils.views import AjaxFormViewMixin


SLUG_MODELS = {
    INGREDIENT_MALT: StockMalt,
    INGREDIENT_HOP: StockHop,
    INGREDIENT_YEAST: StockYeast
}


SLUG_FORMS = {
    INGREDIENT_MALT: StockMaltForm,
    INGREDIENT_HOP: StockHopForm,
    INGREDIENT_YEAST: StockYeastForm
}


# B A S E   V I E W S
# - - - - - - - - - -
# - - - - - - - - - -

class BaseInventoryMixin(object):
    def get_context_data(self, **kwargs):
        context = super(BaseInventoryMixin, self).get_context_data(**kwargs)
        context["ingredients_dict"] = INGREDIENTS_DICT
        return context


class BaseIngredientViewMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if kwargs["ingredient"] not in SLUG_MODELS:
            raise http.Http404
        self.ingredient = kwargs["ingredient"]
        self.model = SLUG_MODELS[kwargs["ingredient"]]
        self.form = SLUG_FORMS[kwargs["ingredient"]]
        return super(BaseIngredientViewMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BaseIngredientViewMixin, self).get_context_data(**kwargs)
        context["ingredient"] = self.ingredient
        context["ingredient_term"] = INGREDIENTS_DICT[self.ingredient]
        return context

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class BaseInventoryIngredientFormMixin(object):
    def get_template_names(self):
        return "inventory/ingredient_form.html"

    def get_form_class(self):
        return self.form

    def get_form_kwargs(self):
        kwargs = super(BaseInventoryIngredientFormMixin, self).get_form_kwargs()
        if not "instance" in kwargs:
            kwargs["instance"] = self.model()
        if not kwargs["instance"]:
            kwargs["instance"] = self.model()
        kwargs["instance"].user = self.request.user
        return kwargs


# - - - - - - - - - -
# - - - - - - - - - -


class InventoryHomeView(BaseInventoryMixin, TemplateView):
    template_name = "inventory/home.html"


class InventoryIngredientView(BaseInventoryMixin, BaseIngredientViewMixin, ListView):
    def get_template_names(self):
        return "inventory/ingredient.html"

    def get_context_object_name(self, object_list):
        return "object_list"


class InventoryIngredientAddView(BaseIngredientViewMixin, BaseInventoryIngredientFormMixin,
                                 BaseInventoryMixin, AjaxFormViewMixin, CreateView):
    pass


class InventoryIngredientUpdateView(BaseIngredientViewMixin, BaseInventoryIngredientFormMixin,
                                    BaseInventoryMixin, AjaxFormViewMixin, UpdateView):
    pass


class InventoryIngredientDeleteView(BaseInventoryMixin, BaseIngredientViewMixin, DeleteView):
    def get_template_names(self):
        return "inventory/ingredient_delete.html"
