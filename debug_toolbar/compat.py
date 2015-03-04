"""
This file exists to contain all Django and Python compatibility issues.

In order to avoid circular references, nothing should be imported from
debug_toolbar.
"""

try:
    from django.template.engine import Engine
except ImportError:  # < Django 1.8
    Engine = None
    from django.template.context import get_standard_processors  #NOQA
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
