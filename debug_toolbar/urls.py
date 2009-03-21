"""
URLpatterns for the debug toolbar. 

These should not be loaded explicitly; the debug toolbar middleware will patch
this into the urlconf for the request.
"""
from django.conf.urls.defaults import *
from django.conf import settings

DEBUG_TB_URL_PREFIX = '__debug__'

urlpatterns = patterns('',
    url(r'^%s/m/(.*)$' % DEBUG_TB_URL_PREFIX, 'debug_toolbar.views.debug_media'),
    url(r'^%s/sql_select/$' % DEBUG_TB_URL_PREFIX, 'debug_toolbar.views.sql_select', name='sql_select'),
    url(r'^%s/sql_explain/$' % DEBUG_TB_URL_PREFIX, 'debug_toolbar.views.sql_explain', name='sql_explain'),
    url(r'^%s/sql_profile/$' % DEBUG_TB_URL_PREFIX, 'debug_toolbar.views.sql_profile', name='sql_profile'),
    url(r'^%s/template_source/$' % DEBUG_TB_URL_PREFIX, 'debug_toolbar.views.template_source', name='template_source'),
)
