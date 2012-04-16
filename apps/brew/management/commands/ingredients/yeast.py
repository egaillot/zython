from django.conf import settings
from brew.models import Yeast
from brew.management.commands.ingredients import xml_import


def flocculation(val):
    return{
        'Low': 1,
        'Medium': 2,
        'High': 3,
        'Very High': 4
    }[val]

def lower_str(val):
    return val.lower()

def do_import():
    xml_file = "%sapps/brew/fixtures/Yeast.xml" % settings.ROOT_PROJECT
    model_class = Yeast
    parent_loop = "YEASTS"
    item_loop = "YEAST"
    fields = (
        ("NAME",        "name"),
        ("LABORATORY",  "laboratory"),
        ("PRODUCT_ID",  "product_id"),
        ("TYPE",        "yeast_type",       lower_str),
        ("FORM",        "form",       lower_str),
        ("FLOCCULATION","flocculation",       flocculation),
        ("ATTENUATION",  "min_attenuation"),
        ("ATTENUATION",  "max_attenuation"),
        ("MIN_TEMPERATURE",  "min_temperature"),
        ("MAX_TEMPERATURE",  "max_temperature"),
        ("BEST_FOR",  "best_for"),
        ("NOTES",  "notes")
    )
    xml_import(xml_file, model_class, parent_loop, item_loop, fields)

