from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic import TemplateView
from brew.views import RecipeListView

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', RecipeListView.as_view(), name='root_url'),
    (r'^brew/', include('brew.urls')),
    (r'^units/', include('units.urls')),
    (r'^accounts/', include('invitation.urls')),
    (r'^accounts/', include('registration_backend.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    url(r'^how-it-works/', TemplateView.as_view(template_name="how.html"), name="how_it_works"),
    (r'^avatar/', include('avatar.urls')),
    
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^admin/', include(admin.site.urls)),
)
