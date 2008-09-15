"""
Helper views for the debug toolbar. These are dynamically installed when the
debug toolbar is displayed, and typically can do Bad Things, so hooking up these
views in any other way is generally not advised.
"""

import os
import django.views.static
from django.conf import settings

def debug_media(request, path):
    root = getattr(settings, 'DEBUG_TOOLBAR_MEDIA_ROOT', None)
    if root is None:
        parent = os.path.abspath(os.path.dirname(__file__))
        root = os.path.join(parent, 'media')
    return django.views.static.serve(request, path, root)