from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

import debug_toolbar

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html")),
    path("jquery/", TemplateView.as_view(template_name="jquery/index.html")),
    path("mootools/", TemplateView.as_view(template_name="mootools/index.html")),
    path("prototype/", TemplateView.as_view(template_name="prototype/index.html")),
    path("admin/", admin.site.urls),
    path("__debug__/", include(debug_toolbar.urls)),
]
