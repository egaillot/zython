from django import forms
from django.forms.models import fields_for_model
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from inspect_model import InspectModel
from brew.models import *
from brew.settings import MAIN_STYLES
from brew.fields import LocalizedModelForm
from units.forms import UnitModelForm
from brew.utils.forms import BS3FormMixin

__all__ = (
    'RecipeForm', 'RecipeMaltForm', 'RecipeHopForm',
    'RecipeMiscForm', 'RecipeYeastForm', 'MashStepForm',
    'RecipeImportForm', 'RecipeSearchForm'
)


def style_choices(qs_kwargs={}):
    old_number = 0
    item = ("", "-------")
    items = []
    for s in BeerStyle.objects.filter(**qs_kwargs).distinct():
        number = s.number
        if old_number != number:
            items.append(item)
            item = [MAIN_STYLES[str(number)], []]
        item[1].append((s.id, "%s" % s))
        old_number = number
    items.append(item)
    return items


class RecipeForm(UnitModelForm, LocalizedModelForm):
    unit_fields = {
        'volume': [
            'batch_size',
            'boiler_tun_deadspace',
            'mash_tun_deadspace'
        ],
        'temperature': ['grain_temperature', ]
    }
    recipe_style = forms.ChoiceField(
        label="Style", choices=style_choices(), required=False)

    def __init__(self, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, **kwargs)
        if self.instance.style:
            self.initial['recipe_style'] = str(self.instance.style.pk)

    def save(self, commit=True, *args, **kwargs):
        recipe = super(RecipeForm, self).save(commit=commit, *args, **kwargs)
        datas = self.cleaned_data
        if datas['recipe_style']:
            recipe.style = BeerStyle.objects.get(pk=datas['recipe_style'])
        if commit:
            recipe.save()
        return recipe

    class Meta:
        model = Recipe
        fields = (
            'name', 'batch_size', 'efficiency', 'private',
            'recipe_style', 'recipe_type',
            'mash_tun_deadspace', 'boiler_tun_deadspace',
            'evaporation_rate', 'grain_temperature'
        )


class RecipeImportForm(forms.Form):
    beer_file = forms.FileField(label=_("Your recipe (BeerXML format)"))


class RecipeIngredientForm(BS3FormMixin, UnitModelForm, LocalizedModelForm):
    pass


class RecipeMaltForm(RecipeIngredientForm):
    unit_fields = {'weight': ['amount', ], 'color': ['color', ]}

    def get_ingredient_list(self):
        return Malt.objects.all()

    def __init__(self, *args, **kwargs):
        super(RecipeMaltForm, self).__init__(*args, **kwargs)

    class Meta:
        model = RecipeMalt
        fields = (
            'amount', 'color',
            'name', 'origin', 'malt_type',
            'potential_gravity', 'malt_yield', 'diastatic_power',
            'protein', 'max_in_batch', 'notes',
        )


class RecipeHopForm(RecipeIngredientForm):
    unit_fields = {'hop': ['amount', ]}

    def get_ingredient_list(self):
        return Hop.objects.all()

    def clean(self):
        data = self.cleaned_data
        if data.get('usage') == "dryhop" and not data.get('dry_days'):
            msg = _("Please enter a number of days of dry hoping")
            self._errors["dry_days"] = self.error_class([msg])
        return data

    class Meta:
        model = RecipeHop
        fields = (
            'amount', 'boil_time', 'dry_days', 'acid_alpha',
            'name', 'origin', 'usage', 'form', 'hop_type',
            'acid_alpha', 'acid_beta', 'notes'
        )


class RecipeMiscForm(RecipeIngredientForm):
    ingredient_name = "misc_id"
    unit_fields = {'hop': ['amount', ]}
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


class MashStepForm(UnitModelForm, LocalizedModelForm):
    unit_fields = {
        'volume': ['water_added', ],
        'temperature': ['temperature', ],
    }

    class Meta:
        model = MashStep
        fields = (
            'name', 'step_type', 'temperature',
            'step_time', 'rise_time', 'water_added'
        )


class RecipeSearchForm(forms.Form):
    style = forms.ChoiceField(
        label=_(u"Style"),
        choices=style_choices(qs_kwargs={'recipe__id__isnull': False}),
        required=False
    )
    q = forms.CharField(required=False)

    def search(self, qs):
        data = self.cleaned_data
        if data['style']:
            qs = qs.filter(style=data['style'])
        if data['q']:
            q = data['q']
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(user__username__icontains=q) |
                Q(style__name__icontains=q) |
                Q(recipemalt__name__icontains=q) |
                Q(recipehop__name__icontains=q) |
                Q(recipemisc__name__icontains=q) |
                Q(recipeyeast__name__icontains=q)
            )
        return qs.distinct()
