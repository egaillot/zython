from django import forms
from django.forms.models import fields_for_model
from inspect_model import InspectModel
from brew.models import *
from brew.settings import MAIN_STYLES
from units.forms import UnitModelForm


__all__ = (
    'RecipeForm', 'RecipeMaltForm', 'RecipeHopForm', 'RecipePreferencesForm', 
    'RecipeMiscForm', 'RecipeYeastForm', 'MashStepForm'
)

def style_choices():
    old_number = None
    item = ("", "-------")
    items = []
    for s in BeerStyle.objects.all():
        number = s.number

        if old_number != number:
            items.append(item)
            item = [MAIN_STYLES[str(number)], []]
        item[1].append((s.id, "%s" % s))
        old_number = number
    return items

class RecipeForm(UnitModelForm):
    unit_fields = {'volume': ['batch_size',]}
    recipe_style = forms.ChoiceField(label="Style", choices=style_choices(), required=False)

    def __init__(self, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, **kwargs)
        if self.instance.style:
            self.initial['recipe_style'] = str(self.instance.style.pk)

    def save(self, *args, **kwargs):
        recipe = super(RecipeForm, self).save(*args, **kwargs)
        datas = self.cleaned_data
        if datas['recipe_style']:
            recipe.style = BeerStyle.objects.get(pk=datas['recipe_style'])
            recipe.save()
        return recipe

    class Meta:
        model = Recipe
        fields = ('name', 'batch_size', 'efficiency', 'private', 'recipe_style', 'recipe_type')


class RecipePreferencesForm(UnitModelForm):
    unit_fields = {'volume': ['boiler_tun_deadspace','mash_tun_deadspace', ], 
                    'temperature': ['grain_temperature', ]}
    class Meta:
        model = Recipe
        fields = ('mash_tun_deadspace', 'boiler_tun_deadspace', 
            'evaporation_rate', 'grain_temperature'
        )


class RecipeIngredientForm(UnitModelForm):
    def __init__(self, *args, **kwargs):
        super(RecipeIngredientForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            fields = fields_for_model(self.instance.__class__)
            unit_fields = self.get_unit_fieldnames()
            for field_name, field in fields.iteritems():
                if field_name not in unit_fields:
                    self.fields[field_name] = field
                    if not self.data:
                        self.initial[field_name] = getattr(self.instance, field_name)
            del self.fields[self.ingredient_name]
            del self.fields["recipe"]
            self.model_fields = list(self.fields.iterkeys())

    def save(self, *args, **kwargs):
        recipe_ingr = self.instance
        add_default = recipe_ingr.pk is None
        if add_default:
            copy_fields = InspectModel(recipe_ingr.__class__).fields
            copy_fields.remove('id')
            base_ingr = self.cleaned_data[self.ingredient_name]
            for field in copy_fields:
                old_value = getattr(recipe_ingr, field, None)
                if add_default:
                    new_value = getattr(base_ingr, field, None)
                    setattr(recipe_ingr, field, new_value)
            for field in self.fields.iterkeys():
                if field != self.ingredient_name:
                    setattr(recipe_ingr, field, self.cleaned_data[field])
            recipe_ingr.save()
        else:
            recipe_ingr = super(RecipeIngredientForm, self).save(*args, **kwargs)
            for f in self.model_fields:
                setattr(recipe_ingr, f, self.cleaned_data[f])
            recipe_ingr.save()
        return recipe_ingr  


class RecipeMaltForm(RecipeIngredientForm):
    ingredient_name = "malt_id"
    unit_fields = {'weight': ['amount',], 'color': ['color',]}
    malt_id = forms.ModelChoiceField(queryset=Malt.objects.all())   

    def __init__(self, *args, **kwargs):
        super(RecipeMaltForm, self).__init__(*args, **kwargs)
        if not self.instance.pk:
            del self.fields['color']

    class Meta:
        model = RecipeMalt
        fields = ('malt_id', 'amount', 'color')


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


class MashStepForm(UnitModelForm):
    unit_fields = {
        'volume': ['water_added',],
        'temperature': ['temperature',],
    }

    class Meta:
        model = MashStep
        fields = (
            'name', 'step_type', 'temperature', 
            'step_time', 'rise_time', 'water_added'
        )

