from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # EXPLAIN SQL via AJAX
    url(r'explain/$', 'debug_toolbar.views.explain', name='explain_sql'),
)
