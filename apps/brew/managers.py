from django.db import models
from django.db.models import Q
from guardian.shortcuts import get_objects_for_user


class RecipeManager(models.Manager):
    def for_user(self, user):
        qs = self.get_query_set()
        if user.is_active:
            special_recipes = get_objects_for_user(user, 'brew.view_recipe')
            qs = qs.filter(
                Q(private=False) |
                Q(user=user) |
                Q(id__in=[r.id for r in special_recipes])
            )
        else:
            qs = qs.filter(private=False)
        return qs
