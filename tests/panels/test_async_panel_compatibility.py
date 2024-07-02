from django.http import HttpResponse
from django.test import AsyncRequestFactory, RequestFactory, TestCase
from django.test.utils import override_settings

from debug_toolbar import settings as dt_settings
from debug_toolbar.toolbar import DebugToolbar


def set_custom_toolbar_config():
    new_settings = dt_settings.get_config().copy()
    new_settings["DISABLE_PANELS"] = {}
    return new_settings


class PanelAsyncCompatibilityTestCase(TestCase):
    def setUp(self):
        self.factory = AsyncRequestFactory()
        self.request = self.factory.get("/")
        self.toolbar = None

    @override_settings(DEBUG_TOOLBAR_CONFIG=set_custom_toolbar_config())
    def test_async_panel_enabling_with_asgi(self):
        self.toolbar = DebugToolbar(self.request, lambda request: HttpResponse())
        for panel in self.toolbar.panels:
            panel.is_async = False
            self.assertFalse(panel.enabled)
            panel.is_async = True
            self.assertTrue(panel.enabled)

    @override_settings(DEBUG_TOOLBAR_CONFIG=set_custom_toolbar_config())
    def test_enable_all_panels_with_wsgi(self):
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.toolbar = DebugToolbar(self.request, lambda request: HttpResponse())
        for panel in self.toolbar.panels:
            panel.is_async = True
            self.assertTrue(panel.enabled)
            panel.is_async = False
            self.assertTrue(panel.enabled)
