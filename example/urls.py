from django.conf import settings
from django.conf.urls import *
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', TemplateView.as_view(template_name='index.html')),
    (r'^jquery/index/$', TemplateView.as_view(template_name='jquery/index.html')),
    (r'^mootools/index/$', TemplateView.as_view(template_name='mootools/index.html')),
    (r'^prototype/index/$', TemplateView.as_view(template_name='prototype/index.html')),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT})
    )

