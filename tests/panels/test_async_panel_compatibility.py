from django.http import HttpResponse
from django.test import AsyncRequestFactory, RequestFactory, TestCase

from debug_toolbar.panels import Panel
from debug_toolbar.toolbar import DebugToolbar


class MockAsyncPanel(Panel):
    is_async = True


class MockSyncPanel(Panel):
    is_async = False


class PanelAsyncCompatibilityTestCase(TestCase):
    def setUp(self):
        self.async_factory = AsyncRequestFactory()
        self.wsgi_factory = RequestFactory()

    def test_panels_with_asgi(self):
        async_request = self.async_factory.get("/")
        toolbar = DebugToolbar(async_request, lambda request: HttpResponse())

        async_panel = MockAsyncPanel(toolbar, async_request)
        sync_panel = MockSyncPanel(toolbar, async_request)

        self.assertTrue(async_panel.enabled)
        self.assertFalse(sync_panel.enabled)

    def test_panels_with_wsgi(self):
        wsgi_request = self.wsgi_factory.get("/")
        toolbar = DebugToolbar(wsgi_request, lambda request: HttpResponse())

        async_panel = MockAsyncPanel(toolbar, wsgi_request)
        sync_panel = MockSyncPanel(toolbar, wsgi_request)

        self.assertTrue(async_panel.enabled)
        self.assertTrue(sync_panel.enabled)
