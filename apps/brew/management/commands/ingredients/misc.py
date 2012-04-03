from django.conf import settings
from brew.models import Misc
from brew.management.commands.ingredients import xml_import


def lower_str(val):
    return val.lower()

def do_import():
    xml_file = "%sapps/brew/fixtures/Misc.xml" % settings.ROOT_PROJECT
    model_class = Misc
    parent_loop = "MISCS"
    item_loop = "MISC"
    fields = (
        ("NAME",     "name"),
        ("TYPE",     "misc_type",       lower_str),
        ("USE_FOR",     "usage"),
        ("USE",         "use_in",       lower_str),
        ("NOTES",     "notes"),
    )
    xml_import(xml_file, model_class, parent_loop, item_loop, fields)
