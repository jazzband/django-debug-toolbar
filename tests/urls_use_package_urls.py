"""urls.py to test using debug_toolbar.urls in include"""

from django.urls import include, path

import debug_toolbar

from . import views

urlpatterns = [
    path("cached_view/", views.cached_view),
    path("__debug__/", include(debug_toolbar.urls)),
]
