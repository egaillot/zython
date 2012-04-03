from django.conf import settings
from brew.models import Malt
from brew.management.commands.ingredients import xml_import

def correct_malt_type(val):
    try:
        return {
            'Dry Extract': 'dryextract',
            'Extract': 'extract',
            'Sugar': 'sugar',
            'Adjunct': 'adjunct',
            'Grain': 'grain',
        }[str(val)]
    except KeyError:
        return 'grain'

def correct_float2(val):
    return "%.2f" % float(val)

def correct_float1(val):
    return "%.1f" % float(val)

def potential_gravity(val):
    return "%.4f" % float(val)

def do_import():
    xml_file = "%sapps/brew/fixtures/Grain.xml" % settings.ROOT_PROJECT
    model_class = Malt
    parent_loop = "FERMENTABLES"
    item_loop = "FERMENTABLE"
    fields = (
        ("NAME",     "name"),
        ("ORIGIN",   "origin"),
        ("TYPE",     "malt_type",    correct_malt_type),
        ("POTENTIAL",     "potential_gravity",    potential_gravity),
        ("YIELD", "malt_yield", correct_float2),
        ("COLOR", "color", correct_float1),
        ("DIASTATIC_POWER", "diastatic_power", correct_float1),
        ("PROTEIN", "protein", correct_float1),
        ("MAX_IN_BATCH", "max_in_batch", correct_float1),
        ("NOTES", "notes")
    
    )
    xml_import(xml_file, model_class, parent_loop, item_loop, fields)
"""
<FERMENTABLES>
    <FERMENTABLE>
     <NAME>Barley Hulls</NAME>
     <VERSION>1</VERSION>
     <TYPE>Adjunct</TYPE>
     <AMOUNT>0.0000000</AMOUNT>
     <YIELD>0.0000000</YIELD>
     <COLOR>0.0000000</COLOR>
     <ADD_AFTER_BOIL>FALSE</ADD_AFTER_BOIL>
     <ORIGIN>US</ORIGIN>
     <SUPPLIER></SUPPLIER>
     <NOTES>Hulls are introduced to improve the speed of lautering when making high gravity or high adjunct beers.
    Hulls are neutral in flavor, body and color, and are inert
    Good for wheat beers, Wits, and others that have high protein mashes.</NOTES>
     <COARSE_FINE_DIFF>1.5000000</COARSE_FINE_DIFF>
     <MOISTURE>4.0000000</MOISTURE>
     <DIASTATIC_POWER>120.0000000</DIASTATIC_POWER>
     <PROTEIN>11.7000000</PROTEIN>
     <MAX_IN_BATCH>5.0000000</MAX_IN_BATCH>
     <RECOMMEND_MASH>FALSE</RECOMMEND_MASH>
     <IBU_GAL_PER_LB>0.0000000</IBU_GAL_PER_LB>
     <DISPLAY_AMOUNT>0.00 kg</DISPLAY_AMOUNT>
     <INVENTORY>0.00 kg</INVENTORY>
     <POTENTIAL>1.0000000</POTENTIAL>
     <DISPLAY_COLOR>0.0 EBC</DISPLAY_COLOR>
     <EXTRACT_SUBSTITUTE></EXTRACT_SUBSTITUTE>
    </FERMENTABLE>
<FERMENTABLES>

"""