import math
from operator import itemgetter
from datetime import datetime
from time import sleep
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User 
from django.contrib.comments.signals import comment_was_posted
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.cache import cache
from public.helpers import send_email_html
from brew.fields import BitternessField, GravityField, ColorField
from brew.models_base import *
from brew import settings as app_settings
from units.conversions import kg_to_lb, ebc_to_srm, \
    srm_to_ebc, l_to_gal, ebc_to_lovibond, g_to_oz, gal_to_l, \
    f_to_c, c_to_f



__all__ = (
    'RECIPE_TYPE_CHOICES', 'MISC_TIME_CHOICES',
    'MASH_TYPE_CHOICES', 'BeerStyle', 'Recipe', 
    'Malt', 'Hop', 'Misc', 'Yeast',
    'RecipeMalt', 'RecipeHop', 'RecipeMisc', 'RecipeYeast',
    'MashStep'
)


RECIPE_TYPE_CHOICES = (
    ('allgrain', _("All grain")),
    ('partial', _("Partial mash")),
    ('extract', _("Extract")),
    ('adjunct', _("Adjunct")),
    ('sugar', _("Sugar"))
)

MISC_TIME_CHOICES = (
    ('min', _('Mins')),
    ('hours', _('Hours')),
    ('days', _('Days')),
    ('weeks', _('Weeks'))
)

MASH_TYPE_CHOICES = (
    ('infusion', _('Infusion')),
    ('decoction', _('Decoction')),
    ('temperature', _('Temperature'))
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


class Recipe(models.Model):
    """
    The main beer recipe
    """
    name = models.CharField(_('Name'), max_length=100)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True, blank=True)
    batch_size = models.DecimalField(_('Batch size'), max_digits=5, decimal_places=1, help_text="L")
    style = models.ForeignKey('BeerStyle', verbose_name=_('Style'), blank=True, null=True)
    recipe_type = models.CharField(_('Type'), choices=RECIPE_TYPE_CHOICES, default="allgrain", max_length=50)
    mes_original_gravity = GravityField(null=True, blank=True)
    mes_final_gravity = GravityField(null=True, blank=True)
    mes_alcohol = models.DecimalField(max_digits=3, decimal_places=1, default="0.0")

    # - - -
    # Preferences
    private = models.BooleanField(_(u'Private recipe ?'), default=False)
    notes = models.TextField(_('Notes'), null=True, blank=True)
    efficiency = models.DecimalField(_('Efficiency'), max_digits=4, decimal_places=1, default="75", help_text="%")
    mash_tun_deadspace = models.DecimalField(_('Mash tun deadspace'), max_digits=5, decimal_places=1, help_text="L", default="1.5")
    boiler_tun_deadspace = models.DecimalField(_('Boiler tun deadspace'), max_digits=5, decimal_places=1, help_text="L", default="1.5")
    evaporation_rate = models.DecimalField(_('Evaporation rate'), max_digits=5, decimal_places=2, help_text="%", default="8")
    grain_temperature = models.DecimalField(_('Grain temperature'), max_digits=3, decimal_places=1, default="22")
    forked_from = models.ForeignKey('self', null=True, blank=True)
    

    # - - -
    # Generic model class/methods

    @property
    def cache_key(self):
        # TODO: 
        # I consider modifying the cache_key system to have a unique 
        # key each time the object is saved.
        modified = self.modified or datetime.now()
        return "%s_%s" % (self.id, modified.strftime('%Y%m%d%H%M%S'))

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('brew_recipe_detail', [str(self.id)])

    class Meta:
        ordering = ('-created',)

    # - - -
    # Water volumes

    def water_initial_mash(self):
        ratio = float(app_settings.WATER_L_PER_GRAIN_KG)
        grain = float(self.get_total_grain())
        return ratio*grain

    def water_pre_boil(self):
        volume = float(self.batch_size) \
            + float(self.boiler_tun_deadspace) \
            + float(self.water_boiloff())
        return volume

    def water_boiloff(self):
        volume = float(self.batch_size + self.boiler_tun_deadspace)
        boil_time = float(self.get_boil_time()+3)/60.
        boil_off = volume*(float(self.evaporation_rate)/100.)*boil_time
        return boil_off

    def water_mash_added(self):
        steps = self.mashstep_set.all()
        if steps.count():
            return float(steps.aggregate(Sum('water_added')).get('water_added__sum'))
        return float(self.water_initial_mash())
    
    def water_grain_absorbtion(self):
        grain_absorbtion = float(self.get_total_grain()) * 1.001
        return grain_absorbtion

    def boil_size(self):
        return self.water_boiloff() + float(self.batch_size) + float(self.boiler_tun_deadspace)

    def water_sparge(self):
        water_sparge = self.water_pre_boil()
        water_sparge += float(self.mash_tun_deadspace)
        water_sparge += float(self.water_grain_absorbtion())
        water_mash = float(self.water_mash_added())
        water_sparge -= water_mash
        return water_sparge

    # - - -
    # Mash 

    def get_total_grain(self):
        cache_key = "%s_total_grain" % self.cache_key
        total = cache.get(cache_key)
        if total is None:
            total = sum(self.recipemalt_set.all().values_list('amount', flat=True))
            cache.set(cache_key, total, 60*15)
        return total

    def get_preboil_gravity(self):
        batch_size = l_to_gal(float(self.batch_size)+float(self.water_boiloff())+float(self.boiler_tun_deadspace))
        return self.get_original_gravity(cache_key="_pbg", batch_size=batch_size)

    def get_original_gravity(self, cache_key="_og", batch_size=None):
        cache_key = "%s%s" % (self.cache_key, cache_key)
        og = cache.get(cache_key)
        if og is None:
            points = []
            if not batch_size:
                batch_size = l_to_gal(self.batch_size)
            efficiency = float(self.efficiency)/100.0
            for grain in self.recipemalt_set.all():
                pounds = kg_to_lb(float(grain.amount))
                gravity = (grain.potential_gravity-1)*1000
                points.append(float(pounds)*float(gravity)*efficiency)
            og = ((sum(points)/batch_size)/1000)+1
            cache.set(cache_key, og, 60*15)
        return "%.3f" % og

    # - - -
    # Coloration

    @property
    def color_image(self):
        srm = int(self.get_srm())
        if srm > 30:
            srm = 30
        return srm

    def get_srm(self):
        cache_key = "%s_get_srm" % self.cache_key
        recipe_srm = cache.get(cache_key)
        if recipe_srm is None:
            grain_srm = []
            batch_size = l_to_gal(float(self.batch_size))
            for grain in self.recipemalt_set.all():
                pounds = kg_to_lb(float(grain.amount))
                lovibond = ebc_to_srm(float(grain.color))
                grain_srm.append(float(lovibond*pounds)/float(batch_size))
            recipe_mcu = float(sum(grain_srm))
            recipe_srm = 1.4922 * (recipe_mcu ** 0.6859)
            cache.set(cache_key, recipe_srm, 60*15)
        return float(recipe_srm)

    def get_ebc(self):
        return srm_to_ebc(self.get_srm())

    def get_hex(self):
        try:
            return app_settings.SRM_TO_HEX[str(int(self.get_srm()))]
        except KeyError:
            return "#000000"

    # - - -
    # Bitterness and spices

    def get_boil_time(self):
        cache_key = "%s_boil_time" % self.cache_key
        boil_time = cache.get(cache_key)
        if boil_time is None:
            hops = self.recipehop_set.all()
            if hops.count():
                boil_time = float(hops[0].boil_time)
            else:
                boil_time = 60.0
            cache.set(cache_key, boil_time, 60*15)
        return boil_time

    def get_ibu(self):
        cache_key = "%s_ibu" % self.cache_key
        ibu = cache.get(cache_key)
        if ibu is None:
            ibu = 0
            for hop in self.recipehop_set.all():
                ibu += hop.ibu()
            cache.set(cache_key, ibu, 60*15)
        return "%.1f" % ibu

    # - - -
    # Bitterness and spices
    
    def get_final_gravity(self):
        cache_key = "%s_fg" % self.cache_key
        fg = cache.get(cache_key)
        if fg is None:
            gravity = (float(float(self.get_original_gravity())-1.)*1000)
            attenuation = 0.75
            yeasts = self.recipeyeast_set.all()
            if yeasts.count():
                yeast = yeasts[0]
                attenuation = float(yeast.attenuation()/100)
            fg = ((gravity-(attenuation*gravity))/1000)+1
            cache.set(cache_key, fg, 60*15)
        return "%.3f" % fg

    def get_abv(self):
        og = float(self.get_original_gravity())
        fg = float(self.get_final_gravity())
        abv = (og-fg)*129.
        return abv

    # - - -
    # Ingredients
    def ingredients(self):
        cache_key = "%s_ingredients" % self.cache_key
        ingredients = cache.get(cache_key)
        if ingredients is None:
            ingredients = []
            # -- Mash -- 
            mash_malt = self.recipemalt_set.all()
            mash_misc = self.recipemisc_set.filter(use_in="mash")
            mash = []
            for malt in mash_malt:
                mash.append({'object':malt, 'weight': malt.amount*1000})
            for misc in mash_misc:
                mash.append({'object':misc, 'weight': misc.amount})
            recipe_mash = sorted(mash, key=itemgetter('weight'), reverse=True)
            for rm in recipe_mash:
                ingredients.append(rm.get('object'))

            # -- Boil -- 
            boil_hops = self.recipehop_set.exclude(usage="dryhop")
            boil_misc = self.recipemisc_set.filter(use_in="boil")
            boil = []
            for hop in boil_hops:
                boil.append({'object':hop, 'duration': hop.get_duration()})
            for misc in boil_misc:
                boil.append({'object':misc, 'duration': misc.get_duration()})
            recipe_boil = sorted(boil, key=itemgetter('duration'), reverse=True)
            for rb in recipe_boil:
                ingredients.append(rb.get('object'))

            # -- Late -- and Fermentables
            late_hops = self.recipehop_set.filter(usage="dryhop")
            late_misc = self.recipemisc_set.exclude(use_in__in=["boil", "mash", "bottling"])
            late = []
            for hop in late_hops:
                late.append({'object':hop, 'duration': hop.get_duration()})
            for misc in late_misc:
                late.append({'object':misc, 'duration': misc.get_duration()})
            recipe_late = sorted(late, key=itemgetter('duration'), reverse=True)
            for rl in recipe_late:
                ingredients.append(rl.get('object'))


            for ry in self.recipeyeast_set.all():
                ingredients.append(ry)

            for rmb in self.recipemisc_set.filter(use_in="bottling"):
                ingredients.append(rmb)
            cache.set(cache_key, ingredients, 60*15)
        return ingredients

class Malt(BaseMalt):
    pass


class Hop(BaseHop):
    pass


class Misc(BaseMisc):
    pass


class Yeast(BaseYeast):
    pass


class UpdateRecipeModel(object):
    def save(self, *args, **kwargs):
        resp = super(UpdateRecipeModel, self).save(*args, **kwargs)
        # Save the recipe so that the cache_key is updated
        self.recipe.save()
        return resp

    def delete(self, *args, **kwargs):
        resp = super(UpdateRecipeModel, self).delete(*args, **kwargs)
        # Save the recipe so that the cache_key is updated
        self.recipe.save()
        return resp


class RecipeMalt(UpdateRecipeModel, BaseMalt):
    recipe = models.ForeignKey('Recipe')
    amount = models.DecimalField(max_digits=5, decimal_places=2, help_text="kg")

    class Meta:
        ordering = ('-amount', 'pk')

    def percent(self):
        total = float(self.recipe.get_total_grain())
        return "%.1f" % ((float(self.amount)/total)*100.)


class RecipeHop(UpdateRecipeModel, BaseHop):
    recipe = models.ForeignKey('Recipe')
    amount = models.DecimalField(max_digits=5, decimal_places=2, help_text="g")
    boil_time = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    dry_days = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)

    def unit_time(self):
        if self.usage == "dryhop":
            return _("%s days") % self.dry_days
        else:
            return "%s min" % self.boil_time

    def get_duration(self):
        # Duration in minutes
        if self.usage == "dryhop":
            return (self.dry_days or 1) * 24 * 60
        else:
            return self.boil_time

    def ibu(self):
        if self.usage == "dryhop":
            return 0
        volume = float(l_to_gal(self.recipe.batch_size))
        gravity = float(self.recipe.get_original_gravity())-1
        alpha = float(float(self.acid_alpha)/100)
        mass = float(g_to_oz(self.amount))
        time = float(self.boil_time)
        mgperl = alpha*mass*7490/volume
        util = 1.65 * (math.pow(0.000125,gravity))*(1-math.exp(-0.04*time))/4.15
        ibu = mgperl*util
        if self.form == "pellets":
            ibu += ibu*0.105
        if self.usage == "firsthop":
            ibu += ibu*0.105
        return ibu


class RecipeYeast(UpdateRecipeModel, BaseYeast):
    recipe = models.ForeignKey('Recipe')


class RecipeMisc(UpdateRecipeModel, BaseMisc):
    recipe = models.ForeignKey('Recipe')
    amount = models.DecimalField(max_digits=5, decimal_places=2, help_text="g")
    time = models.DecimalField(max_digits=4, decimal_places=1)
    time_unit = models.CharField(choices=MISC_TIME_CHOICES, default="mins", max_length=50)

    def get_duration(self):
        # Duration in minutes
        duration = self.time
        if self.time_unit == 'hours':
            return duration * 60
        elif self.time_unit == 'days':
            return duration * 24 * 60
        elif self.time_unit == 'weeks':
            return duration * 7 * 24 * 60
        else:
            return duration


class MashStep(UpdateRecipeModel, models.Model):
    recipe = models.ForeignKey('Recipe')
    ordering = models.IntegerField(default=0)
    name = models.CharField(_("Name"), max_length=100)
    step_type = models.CharField(_("Step type"), choices=MASH_TYPE_CHOICES, max_length=50)
    temperature = models.DecimalField(_("Temperature"), max_digits=4, decimal_places=1)
    step_time = models.IntegerField(_("Step time"), help_text=_("min"))
    rise_time = models.IntegerField(_("Rise time"), help_text=_("min"))
    water_added = models.DecimalField(_("Water added"), max_digits=5, decimal_places=2)

    def initial_heat(self):
        # TODO : 
        # Why doesn't this work properly
        # with total grain weight ??
        # Equation doc : http://www.byo.com/stories/techniques/article/indices/45-mashing/631-feel-the-mash-heat 
        
        Hm = 0.3822 # heat capacity of malt
        Hw = 1.0 # heat capacity of water
        Tmt = 74 # temperature of dry malt
        Tma = float(c_to_f(float(self.temperature))) # temperature of mash step
        M = float(kg_to_lb(self.recipe.get_total_grain())) # weight of malt in lbs
        if M == 0.0:
            M = 1.
        W = float(float(l_to_gal(self.water_added)) * M) # weight of water 
        temp = f_to_c(((M*Hm*(Tma-Tmt))/ (W*Hw)) + Tma)
        return temp

    def set_order(self, direction):
        pass
    
    class Meta:
        ordering = ['ordering',]


# Signal stuffs
def comment_notification(sender, comment, request, *args, **kwargs):
    if comment.content_type == ContentType.objects.get_for_model(Recipe):
        context = {'comment': comment, 'recipe': comment.content_object}
        subject = _(u"New comment posted")
        from_email = settings.DEFAULT_FROM_EMAIL
        template_name = "brew/email/recipe_comment_posted.html"
        to = []
        if comment.content_object.user != request.user:
            to = [comment.content_object.user.email,]
            context['recipe_author'] = False
        else:
            to = list(User.objects.filter(
                    comment_comments__object_pk=comment.object_pk,
                    comment_comments__content_type=comment.content_type,
                    comment_comments__is_removed=False
                ).exclude(
                    id=request.user.id
                ).distinct().values_list('email', flat=True)
            )
            context['recipe_author'] = True
        if to:
            send_email_html(subject, from_email, to, template_name, context=context)
comment_was_posted.connect(comment_notification)
