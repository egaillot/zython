from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from brew.utils.forms import BS3FormMixin
from account.forms import LoginUsernameForm


class ZythonLoginForm(BS3FormMixin, LoginUsernameForm):
    pass


class ZythonSettingForm(BS3FormMixin, UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(ZythonSettingForm, self).__init__(*args, **kwargs)
        del self.fields['password']

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
