# Refresh the debug toolbar's configuration when overriding settings.

from django.dispatch import receiver
from django.test.signals import setting_changed

from debug_toolbar import settings as dt_settings
from debug_toolbar.toolbar import DebugToolbar


@receiver(setting_changed)
def update_toolbar_config(**kwargs):
    if kwargs['setting'] == 'DEBUG_TOOLBAR_CONFIG':
        dt_settings.CONFIG = {}
        dt_settings.CONFIG.update(dt_settings.CONFIG_DEFAULTS)
        dt_settings.CONFIG.update(kwargs['value'] or {})
        # This doesn't account for deprecated configuration options.


@receiver(setting_changed)
def update_toolbar_panels(**kwargs):
    if kwargs['setting'] == 'DEBUG_TOOLBAR_PANELS':
        dt_settings.PANELS = kwargs['value'] or dt_settings.PANELS_DEFAULTS
        DebugToolbar._panel_classes = None
        # Not implemented: invalidate debug_toolbar.urls.
        # This doesn't account for deprecated panel names.
