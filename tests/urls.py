# coding: utf-8

from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib import admin

from .models import NonAsciiRepr


admin.autodiscover()

urlpatterns = patterns('tests.views',
    url(r'^set_session/$', 'set_session'),
    url(r'^resolving1/(.+)/(.+)/$', 'resolving_view', name='positional-resolving'),
    url(r'^resolving2/(?P<arg1>.+)/(?P<arg2>.+)/$', 'resolving_view'),
    url(r'^resolving3/(.+)/$', 'resolving_view', { 'arg2' : 'default' }),
    url(r'^regular/(?P<title>.*)/$', 'regular_view'),
    url(r'^non_ascii_context/$', 'non_ascii_context'),
    url(r'^non_ascii_bytes_in_db_params/$', 'new_user', {'username': 'djàngó'.encode('utf-8')}),
    url(r'^non_ascii_request/$', 'regular_view', {'title': NonAsciiRepr()}),
    url(r'^new_user/$', 'new_user'),
    url(r'^execute_sql/$', 'execute_sql'),
)
