from django.core.exceptions import ImproperlyConfigured

from debug_toolbar.toolbar import debug_toolbar_urls
from tests.base import BaseTestCase


class DebugToolbarUrlsTestCase(BaseTestCase):
    def test_empty_prefix_errors(self):
        with self.assertRaises(ImproperlyConfigured):
            debug_toolbar_urls(prefix="")

    def test_empty_when_debug_is_false(self):
        self.assertEqual(debug_toolbar_urls(), [])

    def test_has_path(self):
        with self.settings(DEBUG=True):
            self.assertEqual(len(debug_toolbar_urls()), 1)
