__all__ = ["VERSION"]


# Do not use pkg_resources to find the version but set it here directly!
# see issue #1446
VERSION = "3.2.1"

# Code that discovers files or modules in INSTALLED_APPS imports this module.

urls = "debug_toolbar.toolbar", "djdt"

default_app_config = "debug_toolbar.apps.DebugToolbarConfig"
