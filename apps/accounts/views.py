from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from accounts.forms import UserEditForm, ZythonLoginForm
import account.views


class LoginView(account.views.LoginView):
    form_class = ZythonLoginForm


class EditUserView(UpdateView):
    template_name = 'accounts/user_form.html'
    form_class = UserEditForm

    def get_success_url(self):
        return ""

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, _(u"Your profile has been updated succesfully"))
        return super(EditUserView, self).form_valid(form)

    def get_object(self):
        return self.request.user

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(EditUserView, self).dispatch(*args, **kwargs)
