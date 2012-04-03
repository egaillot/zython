from django.conf import settings
from brew.models import Hop
from brew.management.commands.ingredients import xml_import


def float2(val):
    return "%.2f" % float(val)

def hop_type(val):
    return val.lower()

def hop_form(val):
    return 'leaf'

def hop_usage(val):
    return 'boil'



def do_import():
    xml_file = "%sapps/brew/fixtures/Hop.xml" % settings.ROOT_PROJECT
    model_class = Hop
    parent_loop = "HOPS"
    item_loop = "HOP"
    fields = (
        ("NAME",     "name"),
        ("ORIGIN",     "origin"),
        ("ALPHA",     "acid_alpha",     float2),
        ("BETA",     "acid_beta",       float2),
        ("USE",     "usage",       hop_usage),
        ("FORM",     "form",       hop_form),
        ("TYPE",     "hop_type",       hop_type),
        ("NOTES",     "notes"),
    )
    xml_import(xml_file, model_class, parent_loop, item_loop, fields)

"""
<HOPS>
    <HOP>
     <NAME>Admiral</NAME>
     <VERSION>1</VERSION>
     <ORIGIN>United Kingdom</ORIGIN>
     <ALPHA>14.7500000</ALPHA>
     <AMOUNT>0.0000000</AMOUNT>
     <USE>Boil</USE>
     <TIME>0.0000000</TIME>
     <NOTES>Bittering hops derived from Wye Challenger.  Good high-alpha bittering hops.
    Used for: Ales
    Aroma: Primarily for bittering
    Substitutes: Target, Northdown, Challenger
    </NOTES>
     <TYPE>Bittering</TYPE>
     <FORM>Pellet</FORM>
     <BETA>5.6000000</BETA>
     <HSI>15.0000000</HSI>
     <DISPLAY_AMOUNT>0.00 g</DISPLAY_AMOUNT>
     <INVENTORY>0.00 g</INVENTORY>
     <DISPLAY_TIME>0.0 min</DISPLAY_TIME>
    </HOP>
</HOPS>
"""
