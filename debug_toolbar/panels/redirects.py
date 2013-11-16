from __future__ import unicode_literals

from django.core.handlers.wsgi import STATUS_CODE_TEXT
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _

from debug_toolbar.panels import DebugPanel


class InterceptRedirectsPanel(DebugPanel):
    """
    Panel that intercepts redirects and displays a page with debug info.
    """
    name = 'Redirects'

    has_content = False

    def enabled(self):
        default = 'on' if self.toolbar.config['INTERCEPT_REDIRECTS'] else 'off'
        return self.toolbar.request.COOKIES.get('djdt' + self.panel_id, default) == 'on'

    def process_response(self, request, response):
        if isinstance(response, HttpResponseRedirect):
            redirect_to = response.get('Location', None)
            if redirect_to:
                try:
                    status_text = STATUS_CODE_TEXT[response.status_code]
                except KeyError:
                    status_text = 'UNKNOWN STATUS CODE'
                status_line = '%s %s' % (response.status_code, status_text.title())
                cookies = response.cookies
                context = {'redirect_to': redirect_to, 'status_line': status_line}
                response = render(request, 'debug_toolbar/redirect.html', context)
                response.cookies = cookies
        return response

    def nav_title(self):
        return _('Intercept redirects')
