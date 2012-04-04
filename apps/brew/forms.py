from django import forms
from django.forms.models import fields_for_model
from inspect_model import InspectModel
from brew.models import *
from units.forms import UnitModelForm


__all__ = (
    'RecipeForm', 'RecipeMaltForm', 'RecipeHopForm', 
    'RecipeMiscForm', 'RecipeYeastForm'
)

class RecipeForm(UnitModelForm):
    unit_fields = {'volume': ['batch_size',]}

    class Meta:
        model = Recipe
        fields = ('name', 'batch_size', 'style', 'recipe_type')


class RecipeIngredientForm(UnitModelForm):
    def __init__(self, *args, **kwargs):
        super(RecipeIngredientForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            fields = fields_for_model(self.instance.__class__)
            for field_name, field in fields.iteritems():
                self.fields[field_name] = field
                if not self.data:
                    self.initial[field_name] = getattr(self.instance, field_name)
            del self.fields[self.ingredient_name]
            del self.fields["recipe"]

    def save(self, *args, **kwargs):
        base_ingr = self.cleaned_data[self.ingredient_name]
        recipe_ingr = self.instance
        copy_fields = InspectModel(recipe_ingr.__class__).fields
        copy_fields.remove('id')
        add_default = recipe_ingr.pk is None
        for field in copy_fields:
            old_value = getattr(recipe_ingr, field, None)
            if add_default:
                new_value = getattr(base_ingr, field, None)
                setattr(recipe_ingr, field, new_value)
        for field in self.Meta.fields:
            if field != self.ingredient_name:
                setattr(recipe_ingr, field, self.cleaned_data[field])
        recipe_ingr.save()
        return recipe_ingr  


class RecipeMaltForm(RecipeIngredientForm):
    ingredient_name = "malt_id"
    unit_fields = {'weight': ['amount',]}
    malt_id = forms.ModelChoiceField(queryset=Malt.objects.all())   

    class Meta:
        model = RecipeMalt
        fields = ('malt_id', 'amount')


class RecipeHopForm(RecipeIngredientForm):
    ingredient_name = "hop_id"
    unit_fields = {'hop': ['amount',]}
    hop_id = forms.ModelChoiceField(queryset=Hop.objects.all())

    class Meta:
        model = RecipeHop
        fields = ('hop_id', 'amount', 'boil_time', 'dry_days')


class RecipeMiscForm(RecipeIngredientForm):
    ingredient_name = "misc_id"
    unit_fields = {'hop': ['amount',]}
    misc_id = forms.ModelChoiceField(queryset=Misc.objects.all())

    class Meta:
        model = RecipeMisc
        fields = ('misc_id', 'amount', 'use_in', 'time', 'time_unit')


class RecipeYeastForm(RecipeIngredientForm):
    ingredient_name = "yeast_id"
    yeast_id = forms.ModelChoiceField(queryset=Yeast.objects.all())

    class Meta:
        model = RecipeYeast
        fields = ('yeast_id', )




