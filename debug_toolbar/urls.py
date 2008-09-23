"""
URLpatterns for the debug toolbar. 

These should not be loaded explicitly; the debug toolbar middleware will patch
this into the urlconf for the request.
"""
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^__debug__/m/(.*)$', 'debug_toolbar.views.debug_media'),
    url(r'^__debug__/sql_explain/$', 'debug_toolbar.views.sql_explain', name='sql_explain'),
)
