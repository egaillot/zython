from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from registration_backend.views import ZythonRegistrationView


urlpatterns = patterns('',
                       url(r'^register/$',
                           ZythonRegistrationView.as_view(),
                           name='registration_register'),
                       url(r'^register/closed/$',
                           TemplateView.as_view(template_name='registration/registration_closed.html'),
                           name='registration_disallowed'),
                       (r'', include('registration.auth_urls')),
                       )
