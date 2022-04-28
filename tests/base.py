import html5lib
from asgiref.local import Local
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase, TransactionTestCase

from debug_toolbar.toolbar import DebugToolbar


class ToolbarTestClient(Client):
    def request(self, **request):
        # Use a thread/async task context-local variable to guard against a
        # concurrent _created signal from a different thread/task.
        data = Local()
        data.toolbar = None

        def handle_toolbar_created(sender, toolbar=None, **kwargs):
            data.toolbar = toolbar

        DebugToolbar._created.connect(handle_toolbar_created)
        try:
            response = super().request(**request)
        finally:
            DebugToolbar._created.disconnect(handle_toolbar_created)
        response.toolbar = data.toolbar

        return response


rf = RequestFactory()


class BaseMixin:
    client_class = ToolbarTestClient

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

    def assertValidHTML(self, content):
        parser = html5lib.HTMLParser()
        parser.parseFragment(content)
        if parser.errors:
            msg_parts = ["Invalid HTML:"]
            lines = content.split("\n")
            for position, errorcode, datavars in parser.errors:
                msg_parts.append("  %s" % html5lib.constants.E[errorcode] % datavars)
                msg_parts.append("    %s" % lines[position[0] - 1])
            raise self.failureException("\n".join(msg_parts))


class BaseTestCase(BaseMixin, TestCase):
    pass


class BaseMultiDBTestCase(BaseMixin, TransactionTestCase):
    databases = {"default", "replica"}


class IntegrationTestCase(TestCase):
    """Base TestCase for tests involving clients making requests."""

    def setUp(self):
        # The HistoryPanel keeps track of previous stores in memory.
        # This bleeds into other tests and violates their idempotency.
        # Clear the store before each test.
        for key in list(DebugToolbar._store.keys()):
            del DebugToolbar._store[key]
        super().setUp()
