from django.conf.urls.defaults import *
from accounts.views import EditUserView

urlpatterns = patterns('',
    url(r'^edit/$', EditUserView.as_view(), name='account_user_edit'),
)