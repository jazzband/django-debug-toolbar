"""
URLpatterns for the debug toolbar.

The debug toolbar middleware will monkey-patch them into the default urlconf
if they aren't explicitly included.
"""

from __future__ import unicode_literals

from django.conf.urls import patterns, url

urlpatterns = patterns('debug_toolbar.views',                           # noqa
    url(r'^render_panel/$', 'render_panel', name='render_panel'),
    url(r'^sql_select/$', 'sql_select', name='sql_select'),
    url(r'^sql_explain/$', 'sql_explain', name='sql_explain'),
    url(r'^sql_profile/$', 'sql_profile', name='sql_profile'),
    url(r'^template_source/$', 'template_source', name='template_source'),
)
