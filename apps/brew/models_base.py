from django.db import models
from brew.fields import BitternessField, GravityField, ColorField

__all__ = (
    'BaseMalt', 'BaseHop', 'BaseYeast', 'BaseMisc', 
    'HOP_USAGE_CHOICES', 'HOP_TYPE_CHOICES', 'YEAST_TYPE_CHOICES',
    'YEAST_FORM_CHOICES', 'YEAST_FLOCCULATION_CHOICES', 'MISC_TYPE_CHOICES', 
    'MALT_TYPE_CHOICES', 'HOP_FORM_CHOICES'
)


MALT_TYPE_CHOICES = (
    ('grain', 'Grain'),
    ('extract', 'Extract'),
    ('dryextract', 'Dry Extract'),
    ('sugar', 'Sugar')
)

HOP_USAGE_CHOICES = (
    ('boil', 'Boil'),
    ('dryhop', 'Dry Hop'),
    ('firsthop', 'First Wort')
)

HOP_FORM_CHOICES = (
    ('leaf', "Leaf"),
    ('pellets', "Pellets"),
    ('plug', "Plug"),
)

HOP_TYPE_CHOICES = (
    ('bittering', "Bittering"),
    ('aroma', "Aroma"),
    ('both', "Both"),
)

YEAST_TYPE_CHOICES = (
    ('ale', 'Ale'),
    ('lager', 'Lager'),
    ('wine', 'Wine'),
    ('champagne', 'Champagne'),
    ('wheat', 'Wheat')
)

YEAST_FORM_CHOICES = (
    ('liguiq', 'Liguid'),
    ('dry', 'Dry'),
    ('culture', 'Culture')
)

YEAST_FLOCCULATION_CHOICES = (
    (1, 'Low'),
    (2, 'Medium'),
    (3, 'High'),
    (4, 'Very high'),
)

MISC_USEIN_CHOICES = (
    ('boil', 'Boil'),
    ('mash', 'Mash'),
    ('primary', 'Primary'),
    ('secondary', 'Secondary'),
    ('bottling', 'Bottling')
)

MISC_TYPE_CHOICES = (
    ('spice','Spice'),
    ('fining','Fining'),
    ('herb','Herb'),
    ('flavor','Flavor'),
    ('other','Other')
)


class BaseMalt(models.Model):
    name = models.CharField(max_length=100)
    origin = models.CharField(max_length=50)
    malt_type = models.CharField(choices=MALT_TYPE_CHOICES, max_length=50)
    
    # Yield
    potential_gravity = GravityField()
    malt_yield = models.DecimalField(max_digits=5, decimal_places=2)

    # Properties
    color = ColorField()
    diastatic_power = models.DecimalField(max_digits=4, decimal_places=1)
    protein = models.DecimalField(max_digits=4, decimal_places=1)
    max_in_batch = models.DecimalField(max_digits=4, decimal_places=1)
    notes = models.TextField(blank=True, null=True)

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
    name = models.CharField(max_length=100)
    origin = models.CharField(max_length=50)
    usage = models.CharField(choices=HOP_USAGE_CHOICES, max_length=10)
    form = models.CharField(choices=HOP_FORM_CHOICES, default="leaf", max_length=50)
    hop_type = models.CharField(choices=HOP_TYPE_CHOICES, max_length=50)
    acid_alpha = models.DecimalField(max_digits=4, decimal_places=2)
    acid_beta = models.DecimalField(max_digits=4, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class BaseYeast(models.Model):
    name = models.CharField(max_length=100)
    laboratory = models.CharField(max_length=100)
    product_id = models.CharField(max_length=100)
    yeast_type = models.CharField(choices=YEAST_TYPE_CHOICES, max_length=50)
    form = models.CharField(choices=YEAST_FORM_CHOICES, max_length=50)
    flocculation = models.CharField(choices=YEAST_FLOCCULATION_CHOICES, max_length=50)
    min_attenuation = models.DecimalField(max_digits=5, decimal_places=2)
    max_attenuation = models.DecimalField(max_digits=5, decimal_places=2)
    min_temperature = models.DecimalField(max_digits=4, decimal_places=1)
    max_temperature = models.DecimalField(max_digits=4, decimal_places=1)
    best_for = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class BaseMisc(models.Model):
    name = models.CharField(max_length=100)
    misc_type = models.CharField(choices=MISC_TYPE_CHOICES, max_length=50)
    usage = models.CharField(max_length=100)
    use_in = models.CharField(choices=MISC_USEIN_CHOICES, default="boil", max_length=50)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True