from django.views.generic import DetailView

from stocks.choices import INGREDIENTS_DICT
from .base import RecipeAuthorMixin, SLUG_MODELROOT


__all__ = ("RecipeDestockView", )


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
                "used_amount": 0,
                "errors": False,
                'recipe_ingredients': []
            }
            for ri in recipeingredients.filter(**{ingredient_slug: stocked_ingredient}):
                data['recipe_ingredients'].append(ri)
                data['remaining_amount'] -= ri.amount
                data['used_amount'] += ri.amount
            if data['remaining_amount'] < 0:
                data['remaining_amount'] = 0
                data["errors"] = True
            datas.append(data)
        return datas

    def get_context_data(self, **kwargs):
        context = super(RecipeDestockView, self).get_context_data(**kwargs)
        self.object = self.get_object()
        ingredients = {}
        for k in INGREDIENTS_DICT.iterkeys():
            ingredients["%ss" % k] = self.previsionnal_stocks_ingredient(k)
        context["ingredients"] = ingredients
        return context
