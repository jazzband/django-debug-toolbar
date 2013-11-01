from __future__ import unicode_literals

try:
    from collections import OrderedDict
except ImportError:
    from django.utils.datastructures import SortedDict as OrderedDict
from django.utils.translation import ugettext_lazy as _
from debug_toolbar.panels import DebugPanel


class HeaderDebugPanel(DebugPanel):
    """
    A panel to display HTTP headers.
    """
    name = 'Header'
    template = 'debug_toolbar/panels/headers.html'
    has_content = True
    # List of environment variables we want to display
    environ_filter = set((
        'CONTENT_LENGTH',
        'CONTENT_TYPE',
        'DJANGO_SETTINGS_MODULE',
        'GATEWAY_INTERFACE',
        'QUERY_STRING',
        'PATH_INFO',
        'PYTHONPATH',
        'REMOTE_ADDR',
        'REMOTE_HOST',
        'REQUEST_METHOD',
        'SCRIPT_NAME',
        'SERVER_NAME',
        'SERVER_PORT',
        'SERVER_PROTOCOL',
        'SERVER_SOFTWARE',
        'TZ',
    ))

    def nav_title(self):
        return _('Headers')

    def title(self):
        return _('Headers')

    def url(self):
        return ''

    def process_request(self, request):
        wsgi_env = list(sorted(request.META.items()))
        self.request_headers = OrderedDict(
            (unmangle(k), v) for (k, v) in wsgi_env if k.startswith('HTTP_'))
        if 'Cookie' in self.request_headers:
            self.request_headers['Cookie'] = '=> see Request Vars panel'
        self.environ = OrderedDict(
            (k, v) for (k, v) in wsgi_env if k in self.environ_filter)

    def process_response(self, request, response):
        self.response_headers = OrderedDict(sorted(response.items()))
        self.record_stats({
            'request_headers': self.request_headers,
            'response_headers': self.response_headers,
            'environ': self.environ,
        })


def unmangle(wsgi_key):
    return wsgi_key[5:].replace('_', '-').title()
