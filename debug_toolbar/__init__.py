import django

from debug_toolbar.urls import app_name

__all__ = ["VERSION"]


# Do not use pkg_resources to find the version but set it here directly!
# see issue #1446
VERSION = "3.2.4"

# Code that discovers files or modules in INSTALLED_APPS imports this module.

urls = "debug_toolbar.urls", app_name

if django.VERSION < (3, 2):
    default_app_config = "debug_toolbar.apps.DebugToolbarConfig"
