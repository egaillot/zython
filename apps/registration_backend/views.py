from registration.views import RegistrationView
from registration_backend.forms import RegistrationForm


class ZythonRegistrationView(RegistrationView):
    form_class = RegistrationForm
    success_url = "/"

    def register(self, request, **cleaned_data):
        user = super(ZythonRegistrationView, self).register(request, **cleaned_data)
        user.is_active = True
        user.first_name = cleaned_data['first_name']
        user.last_name = cleaned_data['last_name']
        user.save()
        return user
