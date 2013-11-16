from __future__ import unicode_literals

from django.template.defaultfilters import slugify
from django.template.loader import render_to_string


class DebugPanel(object):
    """
    Base class for debug panels.
    """
    # name = 'Base'
    # template = 'debug_toolbar/panels/base.html'

    # If content returns something, set to True in subclass
    has_content = False

    # We'll maintain a local context instance so we can expose our template
    # context variables to panels which need them:
    context = {}

    # Panel methods

    def __init__(self, toolbar, context={}):
        self.toolbar = toolbar
        self.context.update(context)
        self.slug = slugify(self.name)

    def content(self):
        if self.has_content:
            context = self.context.copy()
            context.update(self.get_stats())
            return render_to_string(self.template, context)

    @property
    def panel_id(self):
        return self.__class__.__name__

    @property
    def enabled(self):
        return self.toolbar.request.COOKIES.get('djdt' + self.panel_id, 'on') == 'on'

    # URLs for panel-specific views

    @classmethod
    def get_urls(cls):
        return []

    # Titles and subtitles

    def nav_title(self):
        """Title showing in sidebar"""
        raise NotImplementedError

    def nav_subtitle(self):
        """Subtitle showing under title in sidebar"""
        return ''

    def title(self):
        """Title showing in panel"""
        raise NotImplementedError

    # Enable and disable (expensive) instrumentation, must be idempotent

    def enable_instrumentation(self):
        pass

    def disable_instrumentation(self):
        pass

    # Store and retrieve stats (shared between panels)

    def record_stats(self, stats):
        panel_stats = self.toolbar.stats.get(self.slug)
        if panel_stats:
            panel_stats.update(stats)
        else:
            self.toolbar.stats[self.slug] = stats

    def get_stats(self):
        return self.toolbar.stats.get(self.slug, {})

    # Standard middleware methods

    def process_request(self, request):
        pass

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_response(self, request, response):
        pass
