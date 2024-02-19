from django.http import JsonResponse
from django.shortcuts import render


def increment(request):
    try:
        value = int(request.session.get("value", 0)) + 1
    except ValueError:
        value = 1
    request.session["value"] = value
    return JsonResponse({"value": value})


def jinja2_view(request):
    return render(request, "index.jinja", {"foo": "bar"}, using="jinja2")
