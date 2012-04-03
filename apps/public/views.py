# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext


def home(request):
    return render_to_response('public/home.html',
                              {
                                'foo' : "bar",
                              },
                              context_instance=RequestContext(request))
