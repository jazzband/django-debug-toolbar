# coding: utf-8

from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url

import debug_toolbar

from . import views
from .models import NonAsciiRepr

urlpatterns = [
    url(r'^resolving1/(.+)/(.+)/$', views.resolving_view, name='positional-resolving'),
    url(r'^resolving2/(?P<arg1>.+)/(?P<arg2>.+)/$', views.resolving_view),
    url(r'^resolving3/(.+)/$', views.resolving_view, {'arg2': 'default'}),
    url(r'^regular/(?P<title>.*)/$', views.regular_view),
    url(r'^non_ascii_request/$', views.regular_view, {'title': NonAsciiRepr()}),
    url(r'^new_user/$', views.new_user),
    url(r'^execute_sql/$', views.execute_sql),
    url(r'^cached_view/$', views.cached_view),
    url(r'^__debug__/', include(debug_toolbar.urls)),
]
