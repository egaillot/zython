from django import template
from django.db.models.loading import get_model
from django.utils import simplejson as json

register = template.Library()


@register.filter
def humanize_datas(value):
    """Try to humanize the serialized datas from django-reversion"""
    py_val = json.loads(value)[0]
    model = get_model(*py_val['model'].split('.',1))
    fields = py_val['fields']
    error_fields = ('recipe', 'user', 'style')  # Fields that can generate errors are ommited
    for error_field in error_fields:
        if error_field in fields:
            del fields[error_field]
    human_datas = []
    for k, v in fields.items():
        model_field = model._meta.get_field(k)
        human_datas.append({
            'label': str(model_field.verbose_name),
            'value': v,
            'help_text': str(model_field.help_text),
        })
    return human_datas
