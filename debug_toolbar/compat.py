"""
This file exists to contain all Django and Python compatibility issues.

In order to avoid circular references, nothing should be imported from
debug_toolbar.
"""

from django.conf import settings

try:
    from django.core.cache import CacheHandler, caches
except ImportError:  # Django < 1.7
    CacheHandler = None
    caches = None

try:
    from django.template.engine import Engine
except ImportError:  # < Django 1.8
    Engine = None
    from django.template.context import get_standard_processors  # NOQA
    from django.template.loader import find_template_loader  # NOQA

try:
    from importlib import import_module
except ImportError:  # = python 2.6
    from django.utils.importlib import import_module  # NOQA

try:
    from collections import OrderedDict
except ImportError:  # < python 2.7
    from django.utils.datastructures import SortedDict as OrderedDict  # NOQA

try:
    from django.contrib.staticfiles.testing import (
        StaticLiveServerTestCase as LiveServerTestCase)
except ImportError:  # < Django 1.7
    from django.test import LiveServerTestCase  # NOQA

try:
    from django.db.backends import utils
except ImportError:  # >= Django 1.7
    from django.db.backends import util as utils  # NOQA

try:
    from django.dispatch.dispatcher import WEAKREF_TYPES
except ImportError:  # >= Django 1.7
    import weakref
    WEAKREF_TYPES = weakref.ReferenceType,


def get_template_dirs():
    """Compatibility method to fetch the template directories."""
    if Engine:
        template_dirs = Engine.get_default().dirs
    else:  # < Django 1.8
        template_dirs = settings.TEMPLATE_DIRS
    return template_dirs


def get_template_loaders():
    """Compatibility method to fetch the template loaders."""
    if Engine:
        loaders = Engine.get_default().template_loaders
    else:  # < Django 1.8
        loaders = [
            find_template_loader(loader_name)
            for loader_name in settings.TEMPLATE_LOADERS]
    return loaders


def get_template_context_processors():
    """Compatibility method to fetch the template context processors."""
    if Engine:
        context_processors = Engine.get_default().template_context_processors
    else:  # < Django 1.8
        context_processors = get_standard_processors()
    return context_processors
