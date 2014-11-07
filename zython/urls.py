from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.views.generic import TemplateView
from brew.views import RecipeListView
import accounts.views

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', RecipeListView.as_view(), name='root_url'),
    (r'^recipe/', include('brew.urls')),
    (r'^units/', include('units.urls')),
    url(r"^account/login/$", accounts.views.LoginView.as_view(), name="account_signup"),
    url(r"^account/settings/$", accounts.views.SettingsView.as_view(), name="account_settings"),
    url(r"^account/new-social-auth-user/$", accounts.views.new_socialuser, name="account_new_socialuser"),
    url(r"^account/", include("account.urls")),
    (r'^comments/', include('django.contrib.comments.urls')),

    url(r'^comment-delete/(\d+)/', 'public.views.comment_delete', name="comment-delete"),
    url(r'^how-it-works/', TemplateView.as_view(template_name="how.html"), name="how_it_works"),
    url(r'^email_test/', TemplateView.as_view(template_name="base_email.html"), name="dfgfdg"),
    (r'^avatar/', include('avatar.urls')),
    url(r'', include('social_auth.urls')),
    (r'^i18n/', include('django.conf.urls.i18n')),
    (r'^admin/', include(admin.site.urls)),


)
