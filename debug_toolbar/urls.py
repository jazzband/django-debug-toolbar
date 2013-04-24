"""
URLpatterns for the debug toolbar.

These should not be loaded explicitly; the debug toolbar middleware will patch
this into the urlconf for the request.
"""
try:
    from django.conf.urls import patterns, url
except ImportError: # django < 1.4
    from django.conf.urls.defaults import patterns, url

_PREFIX = '__debug__'

urlpatterns = patterns('debug_toolbar.views',
    url(r'^%s/sql_select/$' % _PREFIX, 'sql_select', name='sql_select'),
    url(r'^%s/sql_explain/$' % _PREFIX, 'sql_explain', name='sql_explain'),
    url(r'^%s/sql_profile/$' % _PREFIX, 'sql_profile', name='sql_profile'),
    url(r'^%s/template_source/$' % _PREFIX, 'template_source', name='template_source'),
)
