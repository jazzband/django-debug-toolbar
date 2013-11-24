from __future__ import absolute_import, unicode_literals

import warnings

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


PANELS_DEFAULTS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'debug_toolbar.panels.profiling.ProfilingPanel',
]

try:
    PANELS = list(settings.DEBUG_TOOLBAR_PANELS)
except AttributeError:
    PANELS = PANELS_DEFAULTS
else:
    # Backward-compatibility for 1.0, remove in 2.0.
    _RENAMED_PANELS = {
        'debug_toolbar.panels.version.VersionDebugPanel':
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel':
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings_vars.SettingsDebugPanel':
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel':
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel':
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel':
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel':
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CacheDebugPanel':
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalDebugPanel':
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logger.LoggingDebugPanel':
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.InterceptRedirectsDebugPanel':
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingDebugPanel':
        'debug_toolbar.panels.profiling.ProfilingPanel',
    }
    for index, old_panel in enumerate(PANELS):
        new_panel = _RENAMED_PANELS.get(old_panel)
        if new_panel is not None:
            warnings.warn(
                "%r was renamed to %r. Update your DEBUG_TOOLBAR_PANELS "
                "setting." % (old_panel, new_panel), DeprecationWarning)
            PANELS[index] = new_panel
