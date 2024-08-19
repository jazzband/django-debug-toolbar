from inspect import iscoroutine

from django.template.response import SimpleTemplateResponse
from django.utils.translation import gettext_lazy as _

from debug_toolbar.panels import Panel


class RedirectsPanel(Panel):
    """
    Panel that intercepts redirects and displays a page with debug info.
    """

    has_content = False

    is_async = True

    nav_title = _("Intercept redirects")

    def _process_response(self, response):
        """
        Common response processing logic.
        """
        if 300 <= response.status_code < 400:
            redirect_to = response.get("Location")
            if redirect_to:
                status_line = f"{response.status_code} {response.reason_phrase}"
                cookies = response.cookies
                context = {
                    "redirect_to": redirect_to,
                    "status_line": status_line,
                    "toolbar": self.toolbar,
                }
                # Using SimpleTemplateResponse avoids running global context processors.
                response = SimpleTemplateResponse(
                    "debug_toolbar/redirect.html", context
                )
                response.cookies = cookies
                response.render()
        return response

    async def aprocess_request(self, request, response_coroutine):
        """
        Async version of process_request. used for accessing the response
        by awaiting it when running in ASGI.
        """

        response = await response_coroutine
        return self._process_response(response)

    def process_request(self, request):
        response = super().process_request(request)
        if iscoroutine(response):
            return self.aprocess_request(request, response)
        return self._process_response(response)
