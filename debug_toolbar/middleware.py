"""
Debug Toolbar middleware
"""

import re
import socket
from functools import lru_cache

from django.conf import settings
from django.utils.module_loading import import_string

from debug_toolbar import settings as dt_settings
from debug_toolbar.toolbar import DebugToolbar
from debug_toolbar.utils import clear_stack_trace_caches

_HTML_TYPES = ("text/html", "application/xhtml+xml")


def show_toolbar(request):
    """
    Default function to determine whether to show the toolbar on a given page.
    """
    internal_ips = list(settings.INTERNAL_IPS)

    try:
        # This is a hack for docker installations. It attempts to look
        # up the IP address of the docker host.
        # This is not guaranteed to work.
        docker_ip = (
            # Convert the last segment of the IP address to be .1
            ".".join(socket.gethostbyname("host.docker.internal").rsplit(".")[:-1])
            + ".1"
        )
        internal_ips.append(docker_ip)
    except socket.gaierror:
        # It's fine if the lookup errored since they may not be using docker
        pass
    return settings.DEBUG and request.META.get("REMOTE_ADDR") in internal_ips


@lru_cache(maxsize=None)
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
        if not show_toolbar(request) or DebugToolbar.is_toolbar_request(request):
            return self.get_response(request)

        toolbar = DebugToolbar(request, self.get_response)

        # Activate instrumentation ie. monkey-patch.
        for panel in toolbar.enabled_panels:
            panel.enable_instrumentation()
        try:
            # Run panels like Django middleware.
            response = toolbar.process_request(request)
        finally:
            clear_stack_trace_caches()
            # Deactivate instrumentation ie. monkey-unpatch. This must run
            # regardless of the response. Keep 'return' clauses below.
            for panel in reversed(toolbar.enabled_panels):
                panel.disable_instrumentation()

        # Generate the stats for all requests when the toolbar is being shown,
        # but not necessarily inserted.
        for panel in reversed(toolbar.enabled_panels):
            panel.generate_stats(request, response)
            panel.generate_server_timing(request, response)

        # Always render the toolbar for the history panel, even if it is not
        # included in the response.
        rendered = toolbar.render_toolbar()

        for header, value in self.get_headers(request, toolbar.enabled_panels).items():
            response.headers[header] = value

        # Check for responses where the toolbar can't be inserted.
        content_encoding = response.get("Content-Encoding", "")
        content_type = response.get("Content-Type", "").split(";")[0]
        if (
            getattr(response, "streaming", False)
            or content_encoding != ""
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
    def get_headers(request, panels):
        headers = {}
        for panel in panels:
            for header, value in panel.get_headers(request).items():
                if header in headers:
                    headers[header] += f", {value}"
                else:
                    headers[header] = value
        return headers
