from django.contrib.auth.models import User
from django.http import HttpResponse
from utils import get_request_generator

def execute_sql(request):
    list(User.objects.all())
    
    return HttpResponse()

def resolving_view(request, arg1, arg2):
    # see test_url_resolving in tests.py
    return HttpResponse()

def streaming_http(request, version=1):
    from django.http import StreamingHttpResponse
    return StreamingHttpResponse(get_request_generator(version))
