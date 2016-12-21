# coding: utf-8

from __future__ import absolute_import, unicode_literals

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.cache import cache_page


def execute_sql(request):
    list(User.objects.all())
    return HttpResponse()


def regular_view(request, title):
    return render(request, 'basic.html', {'title': title})


def new_user(request, username='joe'):
    User.objects.create_user(username=username)
    return render(request, 'basic.html', {'title': 'new user'})


def resolving_view(request, arg1, arg2):
    # see test_url_resolving in tests.py
    return HttpResponse()


@cache_page(60)
def cached_view(request):
    return HttpResponse()


def regular_jinjia_view(request, title):
    return render(request, 'jinja2/basic.jinja', {'title': title})
