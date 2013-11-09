# Refresh the debug toolbar's configuration when overriding settings.

from debug_toolbar.utils.settings import CONFIG, CONFIG_DEFAULTS
from debug_toolbar.toolbar.loader import load_panel_classes, panel_classes

from django.dispatch import receiver
from django.test.signals import setting_changed


@receiver(setting_changed)
def update_toolbar_config(**kwargs):
    if kwargs['setting'] == 'DEBUG_TOOLBAR_CONFIG':
        CONFIG.update(CONFIG_DEFAULTS)
        CONFIG.update(kwargs['value'] or {})


@receiver(setting_changed)
def update_toolbar_panels(**kwargs):
    if kwargs['setting'] == 'DEBUG_TOOLBAR_PANELS':
        global panel_classes
        panel_classes = []
        load_panel_classes()
