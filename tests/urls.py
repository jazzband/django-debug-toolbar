from django.urls import include, path, re_path

import debug_toolbar

from . import views
from .models import NonAsciiRepr

urlpatterns = [
    re_path(
        r"^resolving1/(.+)/(.+)/$", views.resolving_view, name="positional-resolving"
    ),
    re_path(r"^resolving2/(?P<arg1>.+)/(?P<arg2>.+)/$", views.resolving_view),
    re_path(r"^resolving3/(.+)/$", views.resolving_view, {"arg2": "default"}),
    re_path(r"^regular/(?P<title>.*)/$", views.regular_view),
    re_path(r"^template_response/(?P<title>.*)/$", views.template_response_view),
    re_path(r"^regular_jinja/(?P<title>.*)/$", views.regular_jinjia_view),
    path("non_ascii_request/", views.regular_view, {"title": NonAsciiRepr()}),
    path("new_user/", views.new_user),
    path("execute_sql/", views.execute_sql),
    path("cached_view/", views.cached_view),
    path("json_view/", views.json_view),
    path("redirect/", views.redirect_view),
    path("__debug__/", include(debug_toolbar.urls)),
]
