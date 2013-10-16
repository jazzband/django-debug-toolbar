"""
URLpatterns for the debug toolbar.

These should not be loaded explicitly; the debug toolbar middleware will patch
this into the urlconf for the request.
"""

from django.conf.urls import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # This pattern should be last to ensure tests still work
    url(r'^resolving1/(.+)/(.+)/$', 'tests.views.resolving_view', name='positional-resolving'),
    url(r'^resolving2/(?P<arg1>.+)/(?P<arg2>.+)/$', 'tests.views.resolving_view'),
    url(r'^resolving3/(.+)/$', 'tests.views.resolving_view', { 'arg2' : 'default' }),
    url(r'^execute_sql/$', 'tests.views.execute_sql'),
)
