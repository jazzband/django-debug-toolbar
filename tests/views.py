from django.contrib.auth.models import User
from django.http import HttpResponse

def execute_sql(request):
    list(User.objects.all())
    
    return HttpResponse()