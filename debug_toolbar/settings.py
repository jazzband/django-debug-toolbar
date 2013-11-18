from __future__ import unicode_literals

from django.conf import settings
from django.utils import six


# Always import this module as follows:
# from debug_toolbar import settings [as dt_settings]

# Don't import directly CONFIG or PANELs, or you will miss changes performed
# with override_settings in tests.


CONFIG_DEFAULTS = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': None,
    'EXTRA_SIGNALS': [],
    'SHOW_COLLAPSED': False,
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
    'RESULTS_CACHE_SIZE': 10,
    'RENDER_PANELS': None,
}


CONFIG = {}
CONFIG.update(CONFIG_DEFAULTS)
CONFIG.update(getattr(settings, 'DEBUG_TOOLBAR_CONFIG', {}))


PANELS_DEFAULTS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.cache.CacheDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    'debug_toolbar.panels.redirects.InterceptRedirectsPanel',
)


PANELS = getattr(settings, 'DEBUG_TOOLBAR_PANELS', PANELS_DEFAULTS)
