"""
The main DebugToolbar class that loads and renders the Toolbar.
"""

import uuid
from collections import OrderedDict
from functools import lru_cache

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.dispatch import Signal
from django.template import TemplateSyntaxError
from django.template.loader import render_to_string
from django.urls import path, resolve
from django.urls.exceptions import Resolver404
from django.utils.module_loading import import_string
from django.utils.translation import get_language, override as lang_override

from debug_toolbar import APP_NAME, settings as dt_settings


class DebugToolbar:
    # for internal testing use only
    _created = Signal()

    def __init__(self, request, get_response):
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
        self._panels = OrderedDict()
        while panels:
            panel = panels.pop()
            self._panels[panel.panel_id] = panel
        self.stats = {}
        self.server_timing_stats = {}
        self.store_id = None
        self.cache_key = "djangodebug_"
        self._created.send(request, toolbar=self)

    # Manage panels

    @property
    def panels(self):
        """
        Get a list of all available panels.
        """
        return list(self._panels.values())

    @property
    def enabled_panels(self):
        """
        Get a list of panels enabled for the current request.
        """
        return [panel for panel in self._panels.values() if panel.enabled]

    def get_panel_by_id(self, panel_id):
        """
        Get the panel with the given id, which is the class name by default.
        """
        return self._panels[panel_id]

    # Handle rendering the toolbar in HTML

    def render_toolbar(self):
        """
        Renders the overall Toolbar with panels inside.
        """
        if not self.should_render_panels():
            self.store()
        if self.tests_run():
            return ""
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
                )
            else:
                raise

    def tests_run(self):
        return self.config.get("TESTS_RUN", False)

    def should_render_panels(self):
        """Determine whether the panels should be rendered during the request

        If False, the panels will be loaded via Ajax.
        """
        render_panels = self.config["RENDER_PANELS"]
        if render_panels is None:
            render_panels = self.request.META["wsgi.multiprocess"]
        return render_panels

    # Handle storing toolbars in memory and fetching them later on

    _store = OrderedDict()

    def store(self):
        # Store already exists.
        if self.store_id:
            return
        self.store_id = uuid.uuid4().hex

        from django.core.cache import cache

        data = {
            "stats": self.stats,
            "server_timing_stats": self.server_timing_stats,
        }

        cache.set(f"{self.cache_key}{self.store_id}", data, self.config["CACHE_TIME"])

    @classmethod
    def fetch(cls, tb, store_id):
        from django.core.cache import cache

        data = cache.get(f"{tb.cache_key}{store_id}")
        if data:
            tb.stats = data.get("stats", {})
            tb.server_timing_stats = data.get("server_timing_stats", {})

            sql_plugin_data = tb.stats.get("SQLPanel")
            if sql_plugin_data:
                databases_data = sql_plugin_data.get("databases", [("default", {})])[0][
                    1
                ]
                tb._panels.get("SQLPanel")._num_queries = databases_data.get(
                    "num_queries"
                )
                tb._panels.get("SQLPanel")._sql_time = sql_plugin_data.get("sql_time")
        tb.store_id = store_id
        return tb

    @classmethod
    def fetch_all(cls, tb):
        import copy

        from django.core.cache import cache

        data_dict = {}
        key_list = cache.keys(f"{tb.cache_key}*")
        for key in key_list:
            store_id = key.split("_")[1]
            data = cache.get(key)
            new_tb = copy.copy(tb)
            new_tb.stats = data["stats"]
            new_tb.server_timing_stats = data["server_timing_stats"]
            new_tb.store_id = store_id
            data_dict[store_id] = new_tb

        return data_dict

    # Manually implement class-level caching of panel classes and url patterns
    # because it's more obvious than going through an abstraction.

    _panel_classes = None

    @classmethod
    def get_panel_classes(cls):
        if cls._panel_classes is None:
            # Load panels in a temporary variable for thread safety.
            panel_classes = [
                import_string(panel_path) for panel_path in dt_settings.get_panels()
            ]
            cls._panel_classes = panel_classes
        return cls._panel_classes

    _urlpatterns = None

    @classmethod
    def get_urls(cls):
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
    def is_toolbar_request(cls, request):
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
        return resolver_match.namespaces and resolver_match.namespaces[-1] == APP_NAME

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


def observe_request(request):
    """
    Determine whether to update the toolbar from a client side request.
    """
    return not DebugToolbar.is_toolbar_request(request)
