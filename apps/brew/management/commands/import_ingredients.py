from django.core.management.base import NoArgsCommand
from brew.management.commands import ingredients
#from brew.models import Malt, Hop, Yeast, BeerStyle


class Command(NoArgsCommand):
    help = "Delete expired user registrations from the database"

    def handle_noargs(self, **options):
        imports = ('malt', 'hop', 'misc', 'style')
        for i in imports:
            print "Proceed %s" % i
            exec("from brew.management.commands.ingredients.%s import do_import" % i)
            do_import()
            print "-"*30
        return ""
