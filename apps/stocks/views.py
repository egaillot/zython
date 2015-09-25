# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, FormView, ListView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
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
