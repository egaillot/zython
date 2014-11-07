from django import http
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from django.contrib import messages

from accounts.forms import ZythonLoginForm, ZythonSettingForm, ZythonSignupForm
from braces.views import LoginRequiredMixin
import account.views


class LoginView(account.views.LoginView):
    form_class = ZythonLoginForm


class SettingsView(LoginRequiredMixin, FormView):
    model = User
    form_class = ZythonSettingForm
    template_name = "account/settings.html"
    success_url = "."

    def get_form_kwargs(self):
        kwargs = super(SettingsView, self).get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.add_message(self.request, messages.SUCCESS, _("Changes saved"))
        return http.HttpResponseRedirect(".")


class SignupView(account.views.SignupView):
    form_class = ZythonSignupForm


def new_socialuser(request):
    messages.add_message(request, messages.SUCCESS, _(u"Welcome to you ! Please review your account settings before using Zython"))
    return http.HttpResponseRedirect("/account/settings/")
