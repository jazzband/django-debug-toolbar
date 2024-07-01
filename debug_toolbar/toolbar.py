"""
The main DebugToolbar class that loads and renders the Toolbar.
"""

import uuid
from collections import OrderedDict
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.dispatch import Signal
from django.http import HttpRequest
from django.template import TemplateSyntaxError
from django.template.loader import render_to_string
from django.urls import URLPattern, path, resolve
from django.urls.exceptions import Resolver404
from django.utils.module_loading import import_string
from django.utils.translation import get_language, override as lang_override

from debug_toolbar import APP_NAME, settings as dt_settings

from ._stubs import GetResponse

if TYPE_CHECKING:
    from .panels import Panel


class DebugToolbar:
    # for internal testing use only
    _created = Signal()

    def __init__(self, request: HttpRequest, get_response: GetResponse):
        self.request = request
        self.config = dt_settings.get_config().copy()
        panels = []
        for panel_class in reversed(self.get_panel_classes()):
            panel = panel_class(self, get_response)
            panels.append(panel)
            if panel.enabled:
                get_response = panel.process_request
        self.process_request = get_response
        # Use OrderedDict for the _panels attribute so that items can be efficiently
        # removed using FIFO order in the DebugToolbar.store() method.  The .popitem()
        # method of Python's built-in dict only supports LIFO removal.
        self._panels = OrderedDict()  # type: ignore[var-annotated]
        while panels:
            panel = panels.pop()
            self._panels[panel.panel_id] = panel
        self.stats: Dict[str, Any] = {}
        self.server_timing_stats: Dict[str, Any] = {}
        self.store_id: Optional[str] = None
        self._created.send(request, toolbar=self)

    # Manage panels

    @property
    def panels(self) -> List["Panel"]:
        """
        Get a list of all available panels.
        """
        return list(self._panels.values())

    @property
    def enabled_panels(self) -> List["Panel"]:
        """
        Get a list of panels enabled for the current request.
        """
        return [panel for panel in self._panels.values() if panel.enabled]

    def get_panel_by_id(self, panel_id: str) -> "Panel":
        """
        Get the panel with the given id, which is the class name by default.
        """
        return self._panels[panel_id]

    # Handle rendering the toolbar in HTML

    def render_toolbar(self) -> str:
        """
        Renders the overall Toolbar with panels inside.
        """
        if not self.should_render_panels():
            self.store()
        try:
            context = {"toolbar": self}
            lang = self.config["TOOLBAR_LANGUAGE"] or get_language()
            with lang_override(lang):
                return render_to_string("debug_toolbar/base.html", context)
        except TemplateSyntaxError:
            if not apps.is_installed("django.contrib.staticfiles"):
                raise ImproperlyConfigured(
                    "The debug toolbar requires the staticfiles contrib app. "
                    "Add 'django.contrib.staticfiles' to INSTALLED_APPS and "
                    "define STATIC_URL in your settings."
                ) from None
            else:
                raise

    def should_render_panels(self) -> bool:
        """Determine whether the panels should be rendered during the request

        If False, the panels will be loaded via Ajax.
        """
        if (render_panels := self.config["RENDER_PANELS"]) is None:
            # If wsgi.multiprocess isn't in the headers, then it's likely
            # being served by ASGI. This type of set up is most likely
            # incompatible with the toolbar until
            # https://github.com/jazzband/django-debug-toolbar/issues/1430
            # is resolved.
            render_panels = self.request.META.get("wsgi.multiprocess", True)
        return render_panels

    # Handle storing toolbars in memory and fetching them later on

    _store = OrderedDict()  # type: ignore[var-annotated]

    def store(self):
        # Store already exists.
        if self.store_id:
            return
        self.store_id = uuid.uuid4().hex
        self._store[self.store_id] = self
        for _ in range(self.config["RESULTS_CACHE_SIZE"], len(self._store)):
            self._store.popitem(last=False)

    @classmethod
    def fetch(cls, store_id):
        return cls._store.get(store_id)

    # Manually implement class-level caching of panel classes and url patterns
    # because it's more obvious than going through an abstraction.

    _panel_classes: Optional[List[Type["Panel"]]] = None

    @classmethod
    def get_panel_classes(cls):
        if cls._panel_classes is None:
            # Load panels in a temporary variable for thread safety.
            panel_classes = [
                import_string(panel_path) for panel_path in dt_settings.get_panels()
            ]
            cls._panel_classes = panel_classes
        return cls._panel_classes

    _urlpatterns: Optional[List[URLPattern]] = None

    @classmethod
    def get_urls(cls) -> List[URLPattern]:
        if cls._urlpatterns is None:
            from . import views

            # Load URLs in a temporary variable for thread safety.
            # Global URLs
            urlpatterns = [
                path("render_panel/", views.render_panel, name="render_panel"),
            ]
            # Per-panel URLs
            for panel_class in cls.get_panel_classes():
                urlpatterns += panel_class.get_urls()
            cls._urlpatterns = urlpatterns
        return cls._urlpatterns

    @classmethod
    def is_toolbar_request(cls, request) -> bool:
        """
        Determine if the request is for a DebugToolbar view.
        """
        # The primary caller of this function is in the middleware which may
        # not have resolver_match set.
        try:
            resolver_match = request.resolver_match or resolve(
                request.path, getattr(request, "urlconf", None)
            )
        except Resolver404:
            return False
        return (
            bool(resolver_match.namespaces)
            and resolver_match.namespaces[-1] == APP_NAME
        )

    @staticmethod
    @lru_cache(maxsize=None)
    def get_observe_request():
        # If OBSERVE_REQUEST_CALLBACK is a string, which is the recommended
        # setup, resolve it to the corresponding callable.
        func_or_path = dt_settings.get_config()["OBSERVE_REQUEST_CALLBACK"]
        if isinstance(func_or_path, str):
            return import_string(func_or_path)
        else:
            return func_or_path


def observe_request(request: HttpRequest):
    """
    Determine whether to update the toolbar from a client side request.
    """
    return True
