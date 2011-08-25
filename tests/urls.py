"""
URLpatterns for the debug toolbar. 

These should not be loaded explicitly; the debug toolbar middleware will patch
this into the urlconf for the request.
"""
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # This pattern should be last to ensure tests still work
    url(r'^execute_sql/$', 'tests.views.execute_sql'),
)
