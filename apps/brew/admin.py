from django.contrib import admin
from brew.models import Malt, Hop, Misc, Yeast, BeerStyle, Recipe, MashStep
import reversion

admin.site.register(Malt)
admin.site.register(Hop)
admin.site.register(Misc)
admin.site.register(Yeast)
admin.site.register(BeerStyle)
admin.site.register(Recipe, reversion.VersionAdmin)
admin.site.register(MashStep)
