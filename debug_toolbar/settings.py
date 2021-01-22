from functools import lru_cache

from django.conf import settings

# Always import this module as follows:
# from debug_toolbar import settings [as dt_settings]

# Don't import directly CONFIG or PANELs, or you will miss changes performed
# with override_settings in tests.


CONFIG_DEFAULTS = {
    # Toolbar options
    "DISABLE_PANELS": {
        "debug_toolbar.panels.profiling.ProfilingPanel",
        "debug_toolbar.panels.redirects.RedirectsPanel",
    },
    "INSERT_BEFORE": "</body>",
    "RENDER_PANELS": None,
    "RESULTS_CACHE_SIZE": 25,
    "ROOT_TAG_EXTRA_ATTRS": "",
    "SHOW_COLLAPSED": False,
    "SHOW_TOOLBAR_CALLBACK": "debug_toolbar.middleware.show_toolbar",
    # Panel options
    "EXTRA_SIGNALS": [],
    "ENABLE_STACKTRACES": True,
    "ENABLE_STACKTRACES_LOCALS": False,
    "HIDE_IN_STACKTRACES": (
        "socketserver",
        "threading",
        "wsgiref",
        "debug_toolbar",
        "django.db",
        "django.core.handlers",
        "django.core.servers",
        "django.utils.decorators",
        "django.utils.deprecation",
        "django.utils.functional",
    ),
    "PRETTIFY_SQL": True,
    "PROFILER_MAX_DEPTH": 10,
    "SHOW_TEMPLATE_CONTEXT": True,
    "SKIP_TEMPLATE_PREFIXES": ("django/forms/widgets/", "admin/widgets/"),
    "SQL_WARNING_THRESHOLD": 500,  # milliseconds
}


@lru_cache()
def get_config():
    USER_CONFIG = getattr(settings, "DEBUG_TOOLBAR_CONFIG", {})
    CONFIG = CONFIG_DEFAULTS.copy()
    CONFIG.update(USER_CONFIG)
    return CONFIG


PANELS_DEFAULTS = [
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
]


@lru_cache()
def get_panels():
    try:
        PANELS = list(settings.DEBUG_TOOLBAR_PANELS)
    except AttributeError:
        PANELS = PANELS_DEFAULTS
    return PANELS
