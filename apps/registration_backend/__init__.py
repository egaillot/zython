from registration.backends.simple import SimpleBackend as RegistrationDefaultBackend
from registration_backend.forms import RegistrationForm


class SimpleBackend(RegistrationDefaultBackend):
    def register(self, request, **kwargs):
        user = super(SimpleBackend, self).register(request, **kwargs)
        user.is_active = True
        user.first_name = kwargs['first_name']
        user.last_name = kwargs['last_name']
        user.save()
        return user

    def get_form_class(self, request):
        return RegistrationForm

    def post_registration_redirect(self, *args, **kwargs):
        return ('root_url', (), {})
