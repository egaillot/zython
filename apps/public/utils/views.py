from django import http


class AjaxFormViewMixin(object):
    def form_valid(self, form):
        form.save()
        resp = http.HttpResponse()
        resp.status_code = 202
        return resp


class FormViewWithRequestMixin(object):
    "Adding request to form kwargs"

    def get_form_kwargs(self):
        kwargs = super(FormViewWithRequestMixin, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs
