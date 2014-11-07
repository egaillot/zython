from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from brew.utils.forms import BS3FormMixin
from account.forms import LoginUsernameForm, SignupForm


class ZythonSignupForm(BS3FormMixin, SignupForm):
    pass


class ZythonLoginForm(BS3FormMixin, LoginUsernameForm):
    pass


class ZythonSettingForm(BS3FormMixin, UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(ZythonSettingForm, self).__init__(*args, **kwargs)
        del self.fields['password']
        self.fields["username"].help_text = u'%s%s' % (_(u"This is what the world will see about you. Choosing a good username is usually a good thing."), self.fields["username"].help_text)
        self.fields["email"].required = True

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
