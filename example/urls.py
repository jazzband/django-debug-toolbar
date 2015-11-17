from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html')),
    url(r'^jquery/$', TemplateView.as_view(template_name='jquery/index.html')),
    url(r'^mootools/$', TemplateView.as_view(template_name='mootools/index.html')),
    url(r'^prototype/$', TemplateView.as_view(template_name='prototype/index.html')),
    url(r'^admin/', include(admin.site.urls)),
]
