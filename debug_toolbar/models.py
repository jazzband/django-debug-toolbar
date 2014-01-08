from __future__ import absolute_import, unicode_literals

from debug_toolbar import settings as dt_settings


if dt_settings.PATCH_SETTINGS:
    dt_settings.patch_all()
