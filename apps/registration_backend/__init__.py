from registration.backends.simple import SimpleBackend as RegistrationDefaultBackend


class SimpleBackend(RegistrationDefaultBackend):
    def register(self, request, **kwargs):
        user = super(DefaultBackend, self).register(request, **kwargs)
        user.is_active = True
        user.save()
        return user

    def post_registration_redirect(self):
        return ('root_url', (), {})

