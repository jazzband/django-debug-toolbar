from django.conf.urls import patterns, include
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = patterns('',                                              # noqa
    (r'^$', TemplateView.as_view(template_name='index.html')),
    (r'^jquery/$', TemplateView.as_view(template_name='jquery/index.html')),
    (r'^mootools/$', TemplateView.as_view(template_name='mootools/index.html')),
    (r'^prototype/$', TemplateView.as_view(template_name='prototype/index.html')),
    (r'^admin/', include(admin.site.urls)),
)
