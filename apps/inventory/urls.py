from django.conf.urls import patterns, url
from .views import InventoryHomeView, InventoryIngredientView, InventoryIngredientAddView,\
    InventoryIngredientUpdateView, InventoryIngredientDeleteView

urlpatterns = patterns(
    '',
    url(r'^$', InventoryHomeView.as_view(), name='inventory_home'),
    url(r'^(?P<ingredient>\w+)/$', InventoryIngredientView.as_view(), name='inventory_ingredient'),
    url(r'^(?P<ingredient>\w+)/add/$', InventoryIngredientAddView.as_view(), name='inventory_ingredient_add'),
    url(r'^(?P<ingredient>\w+)/(?P<pk>\d+)/edit/$', InventoryIngredientUpdateView.as_view(), name='inventory_ingredient_edit'),
    url(r'^(?P<ingredient>\w+)/(?P<pk>\d+)/delete/$', InventoryIngredientDeleteView.as_view(), name='inventory_ingredient_delete'),
)
