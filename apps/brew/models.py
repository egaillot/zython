from django.db import models
from django.contrib.auth.models import User 
from brew.fields import BitternessField, GravityField, ColorField
from brew.models_base import *
from brew.settings import SRM_TO_HEX
from units.conversions import kg_to_lb, ebc_to_srm, \
    srm_to_ebc, l_to_gal, ebc_to_lovibond, g_to_oz

RECIPE_TYPE_CHOICES = (
    ('allgrain', "All grain"),
    ('partial', "Partial mash"),
    ('extract', "Extract"),
    ('adjunct', "Adjunct"),
    ('sugar', "Sugar")
)

MISC_TIME_CHOICES = (
    ('min', 'Mins'),
    ('hours', 'Hours'),
    ('days', 'Days'),
    ('weeks', 'Weeks')
)

MASH_TYPE_CHOICES = (
    ('infusion', 'Infusion'),
    ('decoction', 'Decoction'),
    ('temperature', 'Temperature')
)


class BeerStyle(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    guide = models.CharField(max_length=200)
    number = models.IntegerField()
    sub_number = models.CharField(max_length=1)

    # Ranges
    original_gravity_min = GravityField()
    original_gravity_max = GravityField()
    final_gravity_min = GravityField()
    final_gravity_max = GravityField()
    bitterness_min = BitternessField()
    bitterness_max = BitternessField()
    color_min = ColorField()
    color_max = ColorField()
    alcohol_min = models.DecimalField(max_digits=4, decimal_places=2)
    alcohol_max = models.DecimalField(max_digits=4, decimal_places=2)
    
    # Notes
    description = models.TextField(blank=True, null=True)
    profile = models.TextField(blank=True, null=True)
    ingredients = models.TextField(blank=True, null=True)
    examples = models.TextField(blank=True, null=True)

    def get_number(self):
        return "%s.%s" % (self.number, self.sub_number)

    def __unicode__(self):
        return "%s - %s" % (self.get_number(), self.name)

    class Meta:
        ordering = ('number', 'sub_number')

import math
class Recipe(models.Model):
    """
    The main beer recipe
    """
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)

    # Beer profile
    batch_size = models.DecimalField(max_digits=5, decimal_places=1, help_text="L")
    boil_size = models.DecimalField(max_digits=5, decimal_places=1, default="20.", help_text="L")
    boil_time = models.IntegerField(default=60)
    style = models.ForeignKey('BeerStyle', blank=True, null=True)
    recipe_type = models.CharField(choices=RECIPE_TYPE_CHOICES, default="allgrain", max_length=50)
    est_original_gravity = GravityField(default="1")
    est_final_gravity = GravityField(default="1")
    est_alcohol = models.DecimalField(max_digits=3, decimal_places=1, default="0.0")
    mes_original_gravity = GravityField(null=True, blank=True)
    mes_final_gravity = GravityField(null=True, blank=True)
    mes_alcohol = models.DecimalField(max_digits=3, decimal_places=1, default="0.0")
    color = ColorField(default="0.0")
    bitterness = BitternessField(default="0.0")

    def efficiency(self):
        return 0.78

    def get_total_grain(self):
        return sum(self.recipemalt_set.all().values_list('amount', flat=True))

    def get_srm(self):
        grain_srm = []
        batch_size = l_to_gal(float(self.batch_size))
        for grain in self.recipemalt_set.all():
            pounds = kg_to_lb(float(grain.amount))
            lovibond = ebc_to_srm(float(grain.color))
            grain_srm.append(float(lovibond*pounds)/float(batch_size))
        recipe_mcu = float(sum(grain_srm))
        recipe_srm = 1.4922 * (recipe_mcu ** 0.6859)
        return float(recipe_srm)

    def get_ebc(self):
        return srm_to_ebc(self.get_srm())

    def get_hex(self):
        try:
            return SRM_TO_HEX[str(int(self.get_srm()))]
        except KeyError:
            return "#000000"

    def get_original_gravity(self):
        points = []
        batch_size = l_to_gal(float(self.batch_size))
        efficiency = self.efficiency()
        for grain in self.recipemalt_set.all():
            pounds = kg_to_lb(float(grain.amount))
            gravity = (grain.potential_gravity-1)*1000
            points.append(float(pounds)*float(gravity)*efficiency)
        gravity = ((sum(points)/batch_size)/1000)+1
        return "%.3f" % gravity

    def get_ibu(self):
        bu = 0
        for hop in self.recipehop_set.all():
            bu += hop.ibu()
        return "%.1f" % bu

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('brew_recipe_detail', [str(self.id)])
        


class Malt(BaseMalt):
    pass


class Hop(BaseHop):
    pass


class Misc(BaseMisc):
    pass


class Yeast(BaseYeast):
    pass


class RecipeMalt(BaseMalt):
    recipe = models.ForeignKey('Recipe')
    amount = models.DecimalField(max_digits=5, decimal_places=2, help_text="kg")

    class Meta:
        ordering = ('-amount', 'pk')

    def percent(self):
        total = float(self.recipe.get_total_grain())
        return "%.1f" % ((float(self.amount)/total)*100.)


class RecipeHop(BaseHop):
    recipe = models.ForeignKey('Recipe')
    amount = models.DecimalField(max_digits=5, decimal_places=2, help_text="g")
    boil_time = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    dry_days = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    def ibu(self):
        volume = float(l_to_gal(self.recipe.batch_size))
        gravity = float(self.recipe.get_original_gravity())-1
        alpha = float(float(self.acid_alpha)/100)
        mass = float(g_to_oz(self.amount))
        time = float(self.boil_time)
        mgperl = alpha*mass*7490/volume
        util = 1.65 * (math.pow(0.000125,gravity))*(1-math.exp(-0.04*time))/4.15
        ibu = mgperl*util
        return ibu


class RecipeYeast(BaseYeast):
    recipe = models.ForeignKey('Recipe')


class RecipeMisc(BaseMisc):
    recipe = models.ForeignKey('Recipe')
    amount = models.DecimalField(max_digits=5, decimal_places=2, help_text="g")
    time = models.DecimalField(max_digits=4, decimal_places=1)
    time_unit = models.CharField(choices=MISC_TIME_CHOICES, default="mins", max_length=50)


class MashStep(models.Model):
    recipe = models.ForeignKey('Recipe')
    name = models.CharField(max_length=100)
    step_type = models.CharField(choices=MASH_TYPE_CHOICES, max_length=50)
    temperature = models.DecimalField(max_digits=4, decimal_places=1)
    step_time = models.IntegerField()
    rise_time = models.IntegerField()
    water_added = models.DecimalField(max_digits=5, decimal_places=2)
