"""
Debug Toolbar middleware
"""

import re
from functools import lru_cache

from django.conf import settings
from django.utils.module_loading import import_string

from debug_toolbar import settings as dt_settings
from debug_toolbar.toolbar import DebugToolbar

_HTML_TYPES = ("text/html", "application/xhtml+xml")


def show_toolbar(request):
    """
    Default function to determine whether to show the toolbar on a given page.
    """
    return settings.DEBUG and request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS


@lru_cache()
def get_show_toolbar():
    # If SHOW_TOOLBAR_CALLBACK is a string, which is the recommended
    # setup, resolve it to the corresponding callable.
    func_or_path = dt_settings.get_config()["SHOW_TOOLBAR_CALLBACK"]
    if isinstance(func_or_path, str):
        return import_string(func_or_path)
    else:
        return func_or_path


class DebugToolbarMiddleware:
    """
    Middleware to set up Debug Toolbar on incoming request and render toolbar
    on outgoing response.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Decide whether the toolbar is active for this request.
        show_toolbar = get_show_toolbar()
        if not show_toolbar(request) or request.path.startswith("/__debug__/"):
            return self.get_response(request)

        toolbar = DebugToolbar(request, self.get_response)

        # Activate instrumentation ie. monkey-patch.
        for panel in toolbar.enabled_panels:
            panel.enable_instrumentation()
        try:
            # Run panels like Django middleware.
            response = toolbar.process_request(request)
        finally:
            # Deactivate instrumentation ie. monkey-unpatch. This must run
            # regardless of the response. Keep 'return' clauses below.
            for panel in reversed(toolbar.enabled_panels):
                panel.disable_instrumentation()

        # Generate the stats for all requests when the toolbar is being shown,
        # but not necessarily inserted.
        for panel in reversed(toolbar.enabled_panels):
            panel.generate_stats(request, response)
            panel.generate_server_timing(request, response)

        response = self.generate_server_timing_header(response, toolbar.enabled_panels)

        # Always render the toolbar for the history panel, even if it is not
        # included in the response.
        rendered = toolbar.render_toolbar()

        # Check for responses where the toolbar can't be inserted.
        content_encoding = response.get("Content-Encoding", "")
        content_type = response.get("Content-Type", "").split(";")[0]
        if (
            getattr(response, "streaming", False)
            or "gzip" in content_encoding
            or content_type not in _HTML_TYPES
        ):
            return response

        # Insert the toolbar in the response.
        content = response.content.decode(response.charset)
        insert_before = dt_settings.get_config()["INSERT_BEFORE"]
        pattern = re.escape(insert_before)
        bits = re.split(pattern, content, flags=re.IGNORECASE)
        if len(bits) > 1:
            bits[-2] += rendered
            response.content = insert_before.join(bits)
            if "Content-Length" in response:
                response["Content-Length"] = len(response.content)
        return response

    @staticmethod
    def generate_server_timing_header(response, panels):
        data = []

        for panel in panels:
            stats = panel.get_server_timing_stats()
            if not stats:
                continue

            for key, record in stats.items():
                # example: `SQLPanel_sql_time;dur=0;desc="SQL 0 queries"`
                data.append(
                    '{}_{};dur={};desc="{}"'.format(
                        panel.panel_id, key, record.get("value"), record.get("title")
                    )
                )

        if data:
            response["Server-Timing"] = ", ".join(data)
        return response
