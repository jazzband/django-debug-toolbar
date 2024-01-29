from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_page


def execute_sql(request):
    list(User.objects.all())
    return render(request, "base.html")


def regular_view(request, title):
    return render(request, "basic.html", {"title": title})


def template_response_view(request, title):
    return TemplateResponse(request, "basic.html", {"title": title})


def new_user(request, username="joe"):
    User.objects.create_user(username=username)
    return render(request, "basic.html", {"title": "new user"})


def resolving_view(request, arg1, arg2):
    # see test_url_resolving in tests.py
    return render(request, "base.html")


@cache_page(60)
def cached_view(request):
    return render(request, "base.html")


def cached_low_level_view(request):
    key = "spam"
    value = cache.get(key)
    if not value:
        value = "eggs"
        cache.set(key, value, 60)
    return render(request, "base.html")


def json_view(request):
    return JsonResponse({"foo": "bar"})


def regular_jinjia_view(request, title):
    return render(request, "jinja2/basic.jinja", {"title": title})


def listcomp_view(request):
    lst = [i for i in range(50000) if i % 2 == 0]
    return render(request, "basic.html", {"title": "List comprehension", "lst": lst})


def redirect_view(request):
    return HttpResponseRedirect("/regular/redirect/")


def ajax_view(request):
    return render(request, "ajax/ajax.html")
