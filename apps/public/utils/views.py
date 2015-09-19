from django import http


class AjaxFormViewMixin(object):
    def form_valid(self, form):
        form.save()
        resp = http.HttpResponse()
        resp.status_code = 202
        return resp
