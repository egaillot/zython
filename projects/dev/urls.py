from django.conf.urls.defaults import *
from django.contrib import admin
from brew.views import RecipeListView

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', RecipeListView.as_view(), name='root_url'),
    (r'^brew/', include('brew.urls')),
    (r'^units/', include('units.urls')),
    (r'^accounts/', include('registration.urls')),
    (r'^admin/', include(admin.site.urls)),
)
