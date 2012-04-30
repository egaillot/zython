from django.db import models
from django.utils.translation import ugettext_lazy as _
from brew.fields import BitternessField, GravityField, ColorField

__all__ = (
    'BaseMalt', 'BaseHop', 'BaseYeast', 'BaseMisc', 
    'HOP_USAGE_CHOICES', 'HOP_TYPE_CHOICES', 'YEAST_TYPE_CHOICES',
    'YEAST_FORM_CHOICES', 'YEAST_FLOCCULATION_CHOICES', 'MISC_TYPE_CHOICES', 
    'MALT_TYPE_CHOICES', 'HOP_FORM_CHOICES'
)


MALT_TYPE_CHOICES = (
    ('grain', _('Grain')),
    ('extract', _('Extract')),
    ('dryextract', _('Dry Extract')),
    ('sugar', _('Sugar'))
)

HOP_USAGE_CHOICES = (
    ('boil', _('Boil')),
    ('dryhop', _('Dry Hop')),
    ('firsthop', _('First Wort'))
)

HOP_FORM_CHOICES = (
    ('leaf', _("Leaf")),
    ('pellets', _("Pellets")),
    ('plug', _("Plug")),
)

HOP_TYPE_CHOICES = (
    ('bittering', _("Bittering")),
    ('aroma', _("Aroma")),
    ('both', _("Both")),
)

YEAST_TYPE_CHOICES = (
    ('ale', _('Ale')),
    ('lager', _('Lager')),
    ('wine', _('Wine')),
    ('champagne', _('Champagne')),
    ('wheat', _('Wheat'))
)

YEAST_FORM_CHOICES = (
    ('liquid', _('Liquid')),
    ('dry', _('Dry')),
    ('culture', _('Culture'))
)

YEAST_FLOCCULATION_CHOICES = (
    (1, _('Low')),
    (2, _('Medium')),
    (3, _('High')),
    (4, _('Very high')),
)

MISC_USEIN_CHOICES = (
    ('boil', _('Boil')),
    ('mash', _('Mash')),
    ('primary', _('Primary')),
    ('secondary', _('Secondary')),
    ('bottling', _('Bottling'))
)

MISC_TYPE_CHOICES = (
    ('spice',_('Spice')),
    ('fining',_('Fining')),
    ('herb',_('Herb')),
    ('flavor',_('Flavor')),
    ('other',_('Other'))
)


class BaseMalt(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    origin = models.CharField(_('Origin'), max_length=50)
    malt_type = models.CharField(_('Type'), choices=MALT_TYPE_CHOICES, max_length=50)
    
    # Yield
    potential_gravity = GravityField(_('Potential gravity'), )
    malt_yield = models.DecimalField(_('Yield'), max_digits=5, decimal_places=2, help_text="%")

    # Properties
    color = ColorField(_('Color'), )
    diastatic_power = models.DecimalField(_('Diastatic power'), max_digits=4, decimal_places=1, help_text="Lint.")
    protein = models.DecimalField(_('Protein'), max_digits=4, decimal_places=1, help_text="%")
    max_in_batch = models.DecimalField(_('Max in batch'), max_digits=4, decimal_places=1, help_text="%")
    notes = models.TextField(_('Notes'), blank=True, null=True)

    class Meta:
        abstract = True

    @property
    def copy_fields(self):
        return (
            'name', 'origin', 'malt_type', 'potential_gravity',
            'malt_yield', 'color', 'diastatic_power', 'protein',
            'max_in_batch', 'notes'
        )

class BaseHop(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    origin = models.CharField(_('Origin'), max_length=50)
    usage = models.CharField(_('Usage'), choices=HOP_USAGE_CHOICES, max_length=10)
    form = models.CharField(_('Form'), choices=HOP_FORM_CHOICES, default="leaf", max_length=50)
    hop_type = models.CharField(_('Type'), choices=HOP_TYPE_CHOICES, max_length=50)
    acid_alpha = models.DecimalField(_('Acid alpha'), max_digits=4, decimal_places=2)
    acid_beta = models.DecimalField(_('Acid beta'), max_digits=4, decimal_places=2)
    notes = models.TextField(_('Notes'), blank=True, null=True)

    class Meta:
        abstract = True


class BaseYeast(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    laboratory = models.CharField(_('Lab'), max_length=100)
    product_id = models.CharField(_('Product id'), max_length=100)
    yeast_type = models.CharField(_('Type'), choices=YEAST_TYPE_CHOICES, max_length=50)
    form = models.CharField(_('Form'), choices=YEAST_FORM_CHOICES, max_length=50)
    flocculation = models.CharField(_('Flocculation'), choices=YEAST_FLOCCULATION_CHOICES, max_length=50)
    min_attenuation = models.DecimalField(_('Min attenuation'), max_digits=5, decimal_places=2)
    max_attenuation = models.DecimalField(_('Max attenuation'), max_digits=5, decimal_places=2)
    min_temperature = models.DecimalField(_('Min temperature'), max_digits=4, decimal_places=1)
    max_temperature = models.DecimalField(_('Max temperature'), max_digits=4, decimal_places=1)
    best_for = models.TextField(_('Best for'), null=True, blank=True)
    notes = models.TextField(_('Notes'), null=True, blank=True)

    def attenuation(self):
        return (self.min_attenuation+self.max_attenuation)/2

    class Meta:
        abstract = True


class BaseMisc(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    misc_type = models.CharField(_('Type'), choices=MISC_TYPE_CHOICES, max_length=50)
    usage = models.CharField(_("Usage"), max_length=100, blank=True, null=True)
    use_in = models.CharField(_('Use for'), choices=MISC_USEIN_CHOICES, default="boil", max_length=50)
    notes = models.TextField(_('Notes'), null=True, blank=True)

    class Meta:
        abstract = True