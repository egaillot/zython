from django.db import models
from django import forms


__all__ = (
    'GravityField', 'BitternessField',
    'ColorField', 'LocalizedModelForm'
)


class GravityField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        decimal_places = kwargs.pop('decimal_places', 3)
        max_digits = kwargs.pop('max_digits', 4)
        super(GravityField, self).__init__(
            max_digits=max_digits,
            decimal_places=decimal_places,
            *args, **kwargs
        )


class BitternessField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        decimal_places = kwargs.pop('decimal_places', 1)
        max_digits = kwargs.pop('max_digits', 6)
        super(BitternessField, self).__init__(
            max_digits=max_digits,
            decimal_places=decimal_places,
            *args, **kwargs
        )


class ColorField(models.DecimalField):
    def __init__(self, *args, **kwargs):
        decimal_places = kwargs.pop('decimal_places', 1)
        max_digits = kwargs.pop('max_digits', 7)
        super(ColorField, self).__init__(
            max_digits=max_digits,
            decimal_places=decimal_places,
            *args, **kwargs
        )


class LocalizedModelForm(forms.ModelForm):
    def __new__(cls, *args, **kwargs):
        new_class = super(LocalizedModelForm, cls).__new__(cls)
        for field in new_class.base_fields.values():
            if isinstance(field, forms.DecimalField):
                field.localize = True
                field.widget.is_localized = True
        return new_class
