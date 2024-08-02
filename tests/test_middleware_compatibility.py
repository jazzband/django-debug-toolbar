import asyncio

from django.http import HttpResponse
from django.test import AsyncRequestFactory, RequestFactory, TestCase, override_settings

from debug_toolbar.middleware import DebugToolbarMiddleware


class MiddlewareSyncAsyncCompatibilityTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.async_factory = AsyncRequestFactory()

    @override_settings(DEBUG=True)
    def test_sync_mode(self):
        """
        test middlware switches to sync (__call__) based on get_response type
        """

        request = self.factory.get("/")
        middleware = DebugToolbarMiddleware(
            lambda x: HttpResponse("<html><body>Django debug toolbar</body></html>")
        )

        self.assertFalse(asyncio.iscoroutinefunction(middleware))

        response = middleware(request)
        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    async def test_async_mode(self):
        """
        test middlware switches to async (__acall__) based on get_response type
        and returns a coroutine
        """

        async def get_response(request):
            return HttpResponse("<html><body>Django debug toolbar</body></html>")

        middleware = DebugToolbarMiddleware(get_response)
        request = self.async_factory.get("/")

        self.assertTrue(asyncio.iscoroutinefunction(middleware))

        response = await middleware(request)
        self.assertEqual(response.status_code, 200)
