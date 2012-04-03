from django.conf import settings
from brew.models import BeerStyle
from brew.management.commands.ingredients import xml_import


def lower_str(val):
    return val.lower()

def do_import():
    xml_file = "%sapps/brew/fixtures/Style.xml" % settings.ROOT_PROJECT
    model_class = BeerStyle
    parent_loop = "STYLES"
    item_loop = "STYLE"
    fields = (
        ("NAME",     "name"),
        ("CATEGORY",     "category"),
        ("CATEGORY_NUMBER",     "number"),
        ("STYLE_LETTER",     "sub_number"),
        ("STYLE_GUIDE",     "guide"),
        ("OG_MIN",     "original_gravity_min"),
        ("OG_MAX",     "original_gravity_max"),
        ("FG_MIN",     "final_gravity_min"),
        ("FG_MAX",     "final_gravity_max"),
        ("IBU_MIN",     "bitterness_min"),
        ("IBU_MAX",     "bitterness_max"),
        ("COLOR_MIN",     "color_min"),
        ("COLOR_MAX",     "color_max"),
        ("ABV_MIN",     "alcohol_min"),
        ("ABV_MAX",     "alcohol_max"),
        ("NOTES",     "description"),
        ("PROFILE",     "profile"),
        ("INGREDIENTS",     "ingredients"),
        ("EXAMPLES",     "examples")
    )
    xml_import(xml_file, model_class, parent_loop, item_loop, fields)

