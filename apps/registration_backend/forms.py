from django import forms
from django.utils.translation import ugettext_lazy as _
from registration import forms as reg_forms

class RegistrationForm(reg_forms.RegistrationForm):
    first_name = forms.CharField(label=_('First name'))
    last_name = forms.CharField(label=_('Last name'))

    def __init__(self, *args, **kw):
        super(RegistrationForm, self).__init__(*args, **kw)
        self.fields.keyOrder = [
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2'
        ]

