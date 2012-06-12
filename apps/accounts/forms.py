from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm


class UserEditForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        del self.fields['password']

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')