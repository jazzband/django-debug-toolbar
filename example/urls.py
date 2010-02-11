from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.generic.simple import direct_to_template

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', direct_to_template, {'template': 'index.html'}),
    (r'^jquery/index/$', direct_to_template, {'template': 'jquery/index.html'}),
    (r'^mootools/index/$', direct_to_template, {'template': 'mootools/index.html'}),
    (r'^prototype/index/$', direct_to_template, {'template': 'prototype/index.html'}),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
    )

