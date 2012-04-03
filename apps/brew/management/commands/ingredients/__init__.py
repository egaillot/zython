from lxml import etree

def xml_import(xml_file, model_class, parent_loop, item_loop, fields):
    p = etree.XMLParser(remove_blank_text=True, resolve_entities=False)
    tree = etree.parse(xml_file, p)
    i = 0
    ol = model_class.objects.all()
    ol.delete()
    for item in tree.iterfind(item_loop):
        obj = model_class()
        i += 1
        for f in fields:
            xml_key = f[0]
            field_name = f[1]
            try:
                value = item.find(xml_key).text
                try:
                    custom_func = f[2]
                    value = custom_func(value)
                except IndexError:
                    pass
                setattr(obj, field_name, value)
            except IndexError:
                print "CANT GET FIELD %s on row #%s" % (xml_key, i)
        try:
            obj.save()
            print obj, "saved"
        except:
            print "CANT SAVE row #%s" % i