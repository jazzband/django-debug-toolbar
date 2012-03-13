"""
URLpatterns for the debug toolbar.

These should not be loaded explicitly; the debug toolbar middleware will patch
this into the urlconf for the request.
"""
from django.conf.urls.defaults import *

_PREFIX = '__debug__'

urlpatterns = patterns('',
    url(r'^%s/m/(.*)$' % _PREFIX, 'debug_toolbar.views.debug_media'),
    url(r'^%s/sql_select/$' % _PREFIX, 'debug_toolbar.views.sql_select', name='sql_select'),
    url(r'^%s/sql_explain/$' % _PREFIX, 'debug_toolbar.views.sql_explain', name='sql_explain'),
    url(r'^%s/sql_profile/$' % _PREFIX, 'debug_toolbar.views.sql_profile', name='sql_profile'),
    url(r'^%s/template_source/$' % _PREFIX, 'debug_toolbar.views.template_source', name='template_source'),
)
