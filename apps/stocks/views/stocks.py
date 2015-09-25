# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from public.utils.views import AjaxFormViewMixin
from .base import BaseStockMixin, BaseIngredientViewMixin, BaseStockIngredientFormMixin


class StockHomeView(BaseStockMixin, TemplateView):
    template_name = "stocks/home.html"


class StockIngredientView(BaseStockMixin, BaseIngredientViewMixin, ListView):
    def get_template_names(self):
        return "stocks/ingredient.html"

    def get_context_object_name(self, object_list):
        return "object_list"


class StockIngredientAddView(BaseIngredientViewMixin, BaseStockIngredientFormMixin,
                             BaseStockMixin, AjaxFormViewMixin, CreateView):
    pass


class StockIngredientUpdateView(BaseIngredientViewMixin, BaseStockIngredientFormMixin,
                                BaseStockMixin, AjaxFormViewMixin, UpdateView):
    pass


class StockIngredientDeleteView(BaseStockMixin, BaseIngredientViewMixin, DeleteView):
    def get_success_url(self):
        return reverse("stock_ingredient", args=[self.ingredient, ])

    def get_template_names(self):
        return "stocks/ingredient_delete.html"