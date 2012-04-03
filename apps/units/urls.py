from django.conf.urls.defaults import *
from units import views

urlpatterns = patterns('',
    url(r'^set/(?P<unit>\w+)/(?P<locale>\w+)/$', views.set_unit, name='unit_set'),

)
