"""
The main DebugToolbar class that loads and renders the Toolbar.
"""

from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import patterns, url
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict
from django.utils.importlib import import_module

from debug_toolbar.utils import settings as dt_settings


class DebugToolbar(object):

    def __init__(self, request):
        self.request = request
        self._panels = SortedDict()
        base_url = self.request.META.get('SCRIPT_NAME', '')
        self.config = {}
        self.config.update(dt_settings.CONFIG)
        self.template_context = {
            'BASE_URL': base_url,  # for backwards compatibility
            'STATIC_URL': settings.STATIC_URL,
            'TOOLBAR_ROOT_TAG_ATTRS': self.config['ROOT_TAG_ATTRS'],
        }

        self.load_panels()
        self.stats = {}

    def _get_panels(self):
        return list(self._panels.values())
    panels = property(_get_panels)

    def get_panel(self, cls):
        return self._panels[cls]

    def load_panels(self):
        """
        Populate debug panels
        """
        for panel_class in self.get_panel_classes():
            panel_instance = panel_class(self, context=self.template_context)
            self._panels[panel_class] = panel_instance

    def render_toolbar(self):
        """
        Renders the overall Toolbar with panels inside.
        """
        context = self.template_context.copy()
        context['panels'] = self.panels
        if not self.should_render_panels():
            context['storage_id'] = self.store()
        return render_to_string('debug_toolbar/base.html', context)

    # Handle storing toolbars in memory and fetching them later on

    _counter = 0
    _storage = SortedDict()

    def should_render_panels(self):
        render_panels = dt_settings.CONFIG['RENDER_PANELS']
        if render_panels is None:
            render_panels = self.request.META['wsgi.multiprocess']
        return render_panels

    def store(self):
        cls = type(self)
        cls._counter += 1
        cls._storage[cls._counter] = self
        for _ in range(len(cls._storage) - dt_settings.CONFIG['RESULTS_CACHE_SIZE']):
            # When we drop support for Python 2.6 and switch to
            # collections.OrderedDict, use popitem(last=False).
            del cls._storage[cls._storage.keyOrder[0]]
        return cls._counter

    @classmethod
    def fetch(cls, storage_id):
        return cls._storage.get(storage_id)

    # Manually implement class-level caching of the list of panels because
    # it's more obvious than going through an abstraction.

    _panel_classes = None

    @classmethod
    def get_panel_classes(cls):
        if cls._panel_classes is None:
            # Load panels in a temporary variable for thread safety.
            panel_classes = []
            for panel_path in dt_settings.PANELS:
                # This logic could be replaced with import_by_path in Django 1.6.
                try:
                    panel_module, panel_classname = panel_path.rsplit('.', 1)
                except ValueError:
                    raise ImproperlyConfigured(
                        "%s isn't a debug panel module" % panel_path)
                try:
                    mod = import_module(panel_module)
                except ImportError as e:
                    raise ImproperlyConfigured(
                        'Error importing debug panel %s: "%s"' %
                        (panel_module, e))
                try:
                    panel_class = getattr(mod, panel_classname)
                except AttributeError:
                    raise ImproperlyConfigured(
                        'Toolbar Panel module "%s" does not define a "%s" class' %
                        (panel_module, panel_classname))
                panel_classes.append(panel_class)
            cls._panel_classes = panel_classes
        return cls._panel_classes

    _urlpatterns = None

    @classmethod
    def get_urls(cls):
        if cls._urlpatterns is None:
            # Load URLs in a temporary variable for thread safety.
            # Global URLs
            urlpatterns = patterns('debug_toolbar.views',               # noqa
                url(r'^render_panel/$', 'render_panel', name='render_panel'),
            )
            # Per-panel URLs
            for panel_class in cls.get_panel_classes():
                urlpatterns += panel_class.get_urls()
            cls._urlpatterns = urlpatterns
        return cls._urlpatterns
