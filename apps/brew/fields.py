from django.db import models


__all__ = (
	'GravityField', 'BitternessField', 'ColorField'
)


class GravityField(models.DecimalField):
	def __init__(self, *args, **kwargs):
		super(GravityField, self).__init__(max_digits=4, decimal_places=3, *args, **kwargs)


class BitternessField(models.DecimalField):
	def __init__(self, *args, **kwargs):
		super(BitternessField, self).__init__(max_digits=4, decimal_places=1, *args, **kwargs)


class ColorField(models.DecimalField):
	def __init__(self, *args, **kwargs):
		super(ColorField, self).__init__(max_digits=4, decimal_places=1, *args, **kwargs)



