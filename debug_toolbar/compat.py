"""
This file exists to contain all Django and Python compatibility issues.

In order to avoid circular references, nothing should be imported from
debug_toolbar.
"""

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    from django.template.base import linebreak_iter  # NOQA
except ImportError:  # Django < 1.9
    from django.views.debug import linebreak_iter  # NOQA

try:
    from django.template.engine import Engine
except ImportError:  # Django < 1.8
    Engine = None
    from django.template.context import get_standard_processors  # NOQA
    from django.template.loader import find_template_loader  # NOQA


def get_template_dirs():
    """Compatibility method to fetch the template directories."""
    if Engine:
        try:
            engine = Engine.get_default()
        except ImproperlyConfigured:
            template_dirs = []
        else:
            template_dirs = engine.dirs
    else:  # Django < 1.8
        template_dirs = settings.TEMPLATE_DIRS
    return template_dirs


def get_template_loaders():
    """Compatibility method to fetch the template loaders."""
    if Engine:
        try:
            engine = Engine.get_default()
        except ImproperlyConfigured:
            loaders = []
        else:
            loaders = engine.template_loaders
    else:  # Django < 1.8
        loaders = [
            find_template_loader(loader_name)
            for loader_name in settings.TEMPLATE_LOADERS]
    return loaders


def get_template_context_processors():
    """Compatibility method to fetch the template context processors."""
    if Engine:
        try:
            engine = Engine.get_default()
        except ImproperlyConfigured:
            context_processors = []
        else:
            context_processors = engine.template_context_processors
    else:  # Django < 1.8
        context_processors = get_standard_processors()
    return context_processors
