from __future__ import absolute_import, unicode_literals

import warnings

from django.template.loader import render_to_string


class Panel(object):
    """
    Base class for panels.
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

    # Store and retrieve stats (shared between panels for no good reason)

    def record_stats(self, stats):
        self.toolbar.stats.setdefault(self.panel_id, {}).update(stats)

    def get_stats(self):
        return self.toolbar.stats.get(self.panel_id, {})

    # Standard middleware methods

    def process_request(self, request):
        pass

    def process_view(self, request, view_func, view_args, view_kwargs):
        pass

    def process_response(self, request, response):
        pass


# Backward-compatibility for 1.0, remove in 2.0.
class DebugPanel(Panel):

    def __init__(self, *args, **kwargs):
        warnings.warn("DebugPanel was renamed to Panel.", DeprecationWarning)
        super(DebugPanel, self).__init__(*args, **kwargs)
