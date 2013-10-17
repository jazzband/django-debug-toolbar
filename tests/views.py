from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.http import HttpResponse


def execute_sql(request):
    list(User.objects.all())
    return HttpResponse()


def regular_view(request, title='Test'):
    content = '<html><head><title>%s</title><body></body></html>' % title
    return HttpResponse(content)


def resolving_view(request, arg1, arg2):
    # see test_url_resolving in tests.py
    return HttpResponse()
