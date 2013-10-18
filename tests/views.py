# coding: utf-8

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils import six


def execute_sql(request):
    list(User.objects.all())
    return HttpResponse()


def regular_view(request, title):
    content = '<html><head><title>%s</title><body></body></html>' % title
    return HttpResponse(content)


def resolving_view(request, arg1, arg2):
    # see test_url_resolving in tests.py
    return HttpResponse()


def set_session(request):
    request.session['où'] = 'où'
    if not six.PY3:
        request.session['là'.encode('utf-8')] = 'là'.encode('utf-8')
    return HttpResponse('<html><head><title></title><body></body></html>')
