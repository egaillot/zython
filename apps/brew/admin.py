from django.contrib import admin
from brew.models import Malt, Hop, Misc, Yeast, BeerStyle, Recipe, MashStep


class MaltAdmin(admin.ModelAdmin):
    list_display = ("name", "potential_gravity", "diastatic_power", "malt_yield")


admin.site.register(Malt, MaltAdmin)
admin.site.register(Hop)
admin.site.register(Misc)
admin.site.register(Yeast)
admin.site.register(BeerStyle)
admin.site.register(Recipe)
admin.site.register(MashStep)
