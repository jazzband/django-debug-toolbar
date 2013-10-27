from __future__ import unicode_literals

from django.conf import settings
from django.utils import six


CONFIG_DEFAULTS = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': None,
    'EXTRA_SIGNALS': [],
    'HIDE_DJANGO_SQL': True,
    'SHOW_TEMPLATE_CONTEXT': True,
    'TAG': 'body',
    'ENABLE_STACKTRACES': True,
    'HIDDEN_STACKTRACE_MODULES': (
        'socketserver' if six.PY3 else 'SocketServer',
        'threading',
        'wsgiref',
        'debug_toolbar',
    ),
    'ROOT_TAG_ATTRS': '',
    'SQL_WARNING_THRESHOLD': 500,   # milliseconds
}


CONFIG = {}
CONFIG.update(CONFIG_DEFAULTS)
CONFIG.update(getattr(settings, 'DEBUG_TOOLBAR_CONFIG', {}))
