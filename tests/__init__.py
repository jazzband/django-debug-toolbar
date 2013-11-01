# Refresh the debug toolbar's configuration when overriding settings.

from debug_toolbar.utils.settings import CONFIG, CONFIG_DEFAULTS
from django.dispatch import receiver
from django.test.signals import setting_changed


@receiver(setting_changed)
def update_toolbar_config(**kwargs):
    if kwargs['setting'] == 'DEBUG_TOOLBAR_CONFIG':
        CONFIG.update(CONFIG_DEFAULTS)
        CONFIG.update(kwargs['value'] or {})
