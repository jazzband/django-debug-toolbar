"""
URLpatterns for the debug toolbar.

These should not be loaded explicitly; the debug toolbar middleware will patch
this into the urlconf for the request.
"""

from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('tests.views',
    url(r'^resolving1/(.+)/(.+)/$', 'resolving_view', name='positional-resolving'),
    url(r'^resolving2/(?P<arg1>.+)/(?P<arg2>.+)/$', 'resolving_view'),
    url(r'^resolving3/(.+)/$', 'resolving_view', { 'arg2' : 'default' }),
    url(r'^regular/(?P<title>.*)/$', 'regular_view'),
    url(r'^execute_sql/$', 'execute_sql'),
)
