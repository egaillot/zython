import time
from cStringIO import StringIO
from lxml import etree
from brew.models import Recipe, RecipeHop, RecipeMalt,\
    RecipeMisc, RecipeYeast, MashStep, BeerStyle
from brew.beer_xml import FERMENTABLE_FIELDS, HOP_FIELDS,\
    MISC_FIELDS, YEAST_FIELDS


def populate_object(xml_item, object, fields):
    for f in fields:
        xml_key = f[0]
        field_name = f[1]
        try:
            value = xml_item.find(xml_key).text
            try:
                custom_func = f[2]
                value = custom_func(value)
            except IndexError:
                pass
            setattr(object, field_name, value)
        except IndexError:
            print "CANT GET FIELD %s" % xml_key
    return object


def xml_import(xml_file, model_class, parent_loop, item_loop, fields):
    p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
    tree = etree.parse(xml_file, p)
    i = 0
    ol = model_class.objects.all()
    ol.delete()
    for item in tree.iterfind(item_loop):
        obj = model_class()
        i += 1
        populate_object(item, obj, fields)
        try:
            obj.save()
            print obj, "saved"
        except:
            print "CANT SAVE row #%s" % i


def kg_to_g(val):
    return str(float(val) * 1000.)


def import_beer_xml(datas, user):
    datas = datas.replace(
        "<RECIPES>",
        """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" ><RECIPES>"""
    )
    p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
    tree = etree.parse(StringIO(datas), p)
    recipes = []
    for nodes in tree.iter('RECIPES'):
        for node in nodes.iter('RECIPE'):
            recipe = Recipe(user=user)
            recipe.name = node.find("NAME").text
            recipe.batch_size = node.find("BATCH_SIZE").text
            recipe.efficiency = node.find("EFFICIENCY").text
            recipe.notes = node.find("NOTES").text
            recipe.recipe_type = {
                "All Grain": "allgrain",
                "Extract": "extract",
                "Partial Mash": "partial"
            }.get(node.find("TYPE").text, "allgrain")
            recipe.created = time.strptime(node.find("DATE").text, "%d/%m/%Y")
            equipment = node.find("EQUIPMENT")
            recipe.evaporation_rate = equipment.find("EVAP_RATE").text
            recipe.mash_tun_deadspace = equipment.find("LAUTER_DEADSPACE").text
            recipe.boiler_tun_deadspace = equipment.find("TRUB_CHILLER_LOSS").text
            mash = node.find("MASH")
            recipe.grain_temperature = mash.find('GRAIN_TEMP').text
            style = node.find("STYLE")
            style_num = style.find('CATEGORY_NUMBER').text
            style_let = style.find('STYLE_LETTER').text
            try:
                bs = BeerStyle.objects.filter(
                    number=style_num, sub_number=style_let
                )[0]
                recipe.style = bs
            except IndexError:
                pass

            recipe.save()

            MALTS = list(FERMENTABLE_FIELDS) + [("AMOUNT", "amount"), ]
            HOPS = list(HOP_FIELDS) + [
                ("AMOUNT", "amount", kg_to_g),
                ("TIME", "boil_time")
            ]
            MISCS = list(MISC_FIELDS) + [
                ("AMOUNT", "amount", kg_to_g),
                ("TIME", "time")
            ]
            ingredients = (
                ("FERMENTABLES", "FERMENTABLE", RecipeMalt, MALTS),
                ("HOPS", "HOP", RecipeHop, HOPS),
                ("MISCS", "MISC", RecipeMisc, MISCS),
                ("YEASTS", "YEAST", RecipeYeast, YEAST_FIELDS),
            )

            for i in ingredients:
                ingr_list = node.find(i[0])
                if ingr_list:
                    for ingr in ingr_list.iterfind(i[1]):
                        recipe_ingr = i[2](recipe=recipe)
                        recipe_ingr = populate_object(ingr, recipe_ingr, i[3])
                        recipe_ingr.save()
            ordering = 0
            mash_steps = mash.find('MASH_STEPS')
            for step in mash_steps.iterfind('MASH_STEP'):
                ordering += 1
                mash_step = MashStep(recipe=recipe)
                mash_step.ordering = ordering
                mash_step.name = step.find('NAME').text
                mash_step.step_type = step.find('TYPE').text.lower()
                mash_step.temperature = step.find('STEP_TEMP').text
                mash_step.step_time = step.find('STEP_TIME').text.split('.')[0]
                mash_step.rise_time = step.find('RAMP_TIME').text.split('.')[0]
                mash_step.water_added = step.find('INFUSE_AMOUNT').text
                mash_step.save()
            recipes.append(recipe)
    return recipes
