import html5lib
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from debug_toolbar.toolbar import DebugToolbar

rf = RequestFactory()


class BaseTestCase(TestCase):
    panel_id = None

    def setUp(self):
        super().setUp()
        self._get_response = lambda request: HttpResponse()
        self.request = rf.get("/")
        self.toolbar = DebugToolbar(self.request, self.get_response)
        self.toolbar.stats = {}

        if self.panel_id:
            self.panel = self.toolbar.get_panel_by_id(self.panel_id)
            self.panel.enable_instrumentation()
        else:
            self.panel = None

    def tearDown(self):
        if self.panel:
            self.panel.disable_instrumentation()
        super().tearDown()

    def get_response(self, request):
        return self._get_response(request)

    def assertValidHTML(self, content, msg=None):
        parser = html5lib.HTMLParser()
        parser.parseFragment(self.panel.content)
        if parser.errors:
            default_msg = ["Content is invalid HTML:"]
            lines = content.split("\n")
            for position, errorcode, datavars in parser.errors:
                default_msg.append("  %s" % html5lib.constants.E[errorcode] % datavars)
                default_msg.append("    %s" % lines[position[0] - 1])

            msg = self._formatMessage(msg, "\n".join(default_msg))
            raise self.failureException(msg)
