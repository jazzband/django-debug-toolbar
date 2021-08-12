import inspect

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Warning, register
from django.middleware.gzip import GZipMiddleware
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from debug_toolbar import settings as dt_settings


class DebugToolbarConfig(AppConfig):
    name = "debug_toolbar"
    verbose_name = _("Debug Toolbar")


@register
def check_middleware(app_configs, **kwargs):
    from debug_toolbar.middleware import DebugToolbarMiddleware

    errors = []
    gzip_index = None
    debug_toolbar_indexes = []
    postgres_app_index = None
    debug_toolbar_app_index = None

    # If old style MIDDLEWARE_CLASSES is being used, report an error.
    if settings.is_overridden("MIDDLEWARE_CLASSES"):
        errors.append(
            Warning(
                "debug_toolbar is incompatible with MIDDLEWARE_CLASSES setting.",
                hint="Use MIDDLEWARE instead of MIDDLEWARE_CLASSES",
                id="debug_toolbar.W004",
            )
        )
        return errors

    # Determine the indexes which gzip and/or the toolbar are installed at
    for i, middleware in enumerate(settings.MIDDLEWARE):
        if is_middleware_class(GZipMiddleware, middleware):
            gzip_index = i
        elif is_middleware_class(DebugToolbarMiddleware, middleware):
            debug_toolbar_indexes.append(i)

    postgres_apps = [
        "django.contrib.postgres",
        "django.contrib.postgres.apps.PostgresConfig",
    ]
    debug_toolbar_apps = [
        "debug_toolbar",
        "debug_toolbar.apps.DebugToolbarConfig",
    ]
    for i, installed_app in enumerate(settings.INSTALLED_APPS):
        if installed_app in postgres_apps:
            postgres_app_index = i
        elif installed_app in debug_toolbar_apps:
            debug_toolbar_app_index = i

    if not debug_toolbar_indexes:
        # If the toolbar does not appear, report an error.
        errors.append(
            Warning(
                "debug_toolbar.middleware.DebugToolbarMiddleware is missing "
                "from MIDDLEWARE.",
                hint="Add debug_toolbar.middleware.DebugToolbarMiddleware to "
                "MIDDLEWARE.",
                id="debug_toolbar.W001",
            )
        )
    elif len(debug_toolbar_indexes) != 1:
        # If the toolbar appears multiple times, report an error.
        errors.append(
            Warning(
                "debug_toolbar.middleware.DebugToolbarMiddleware occurs "
                "multiple times in MIDDLEWARE.",
                hint="Load debug_toolbar.middleware.DebugToolbarMiddleware only "
                "once in MIDDLEWARE.",
                id="debug_toolbar.W002",
            )
        )
    elif gzip_index is not None and debug_toolbar_indexes[0] < gzip_index:
        # If the toolbar appears before the gzip index, report an error.
        errors.append(
            Warning(
                "debug_toolbar.middleware.DebugToolbarMiddleware occurs before "
                "django.middleware.gzip.GZipMiddleware in MIDDLEWARE.",
                hint="Move debug_toolbar.middleware.DebugToolbarMiddleware to "
                "after django.middleware.gzip.GZipMiddleware in MIDDLEWARE.",
                id="debug_toolbar.W003",
            )
        )

    if (
        debug_toolbar_app_index is not None
        and postgres_app_index is not None
        and postgres_app_index > debug_toolbar_app_index
    ):
        errors.append(
            Warning(
                "django.contrib.postgres occurs after django_toolbar in INSTALLED_APPS. This can lead to `can't adapt type 'dict'` messages.",
                hint="Move django.contrib.postgres to before django_toolbar in INSTALLED_APPS.",
                id="debug_toolbar.W006",
            )
        )
    return errors


@register
def check_panel_configs(app_configs, **kwargs):
    """Allow each panel to check the toolbar's integration for their its own purposes."""
    from debug_toolbar.toolbar import DebugToolbar

    errors = []
    for panel_class in DebugToolbar.get_panel_classes():
        for check_message in panel_class.run_checks():
            errors.append(check_message)
    return errors


def is_middleware_class(middleware_class, middleware_path):
    try:
        middleware_cls = import_string(middleware_path)
    except ImportError:
        return
    return inspect.isclass(middleware_cls) and issubclass(
        middleware_cls, middleware_class
    )


@register
def check_panels(app_configs, **kwargs):
    errors = []
    panels = dt_settings.get_panels()
    if not panels:
        errors.append(
            Warning(
                "Setting DEBUG_TOOLBAR_PANELS is empty.",
                hint="Set DEBUG_TOOLBAR_PANELS to a non-empty list in your "
                "settings.py.",
                id="debug_toolbar.W005",
            )
        )
    return errors
