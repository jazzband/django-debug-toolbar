"""
This file exists to contain all Django and Python compatibility issues.

In order to avoid circular references, nothing should be imported from
debug_toolbar.
"""

try:
    from django.template.base import linebreak_iter  # NOQA
except ImportError:  # Django < 1.9
    from django.views.debug import linebreak_iter  # NOQA
