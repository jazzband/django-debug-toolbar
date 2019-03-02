import logging

from debug_toolbar.panels.logging import (
    MESSAGE_IF_STRING_REPRESENTATION_INVALID,
    collector,
)

from ..base import BaseTestCase
from ..views import regular_view


class LoggingPanelTestCase(BaseTestCase):
    panel_id = "LoggingPanel"

    def setUp(self):
        super().setUp()
        self.logger = logging.getLogger(__name__)
        collector.clear_collection()

        # Assume the root logger has been configured with level=DEBUG.
        # Previously DDT forcefully set this itself to 0 (NOTSET).
        logging.root.setLevel(logging.DEBUG)

    def test_happy_case(self):
        def view(request):
            self.logger.info("Nothing to see here, move along!")
            return regular_view(request, "logging")

        self._get_response = view
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        records = self.panel.get_stats()["records"]

        self.assertEqual(1, len(records))
        self.assertEqual("Nothing to see here, move along!", records[0]["message"])

    def test_formatting(self):
        def view(request):
            self.logger.info("There are %d %s", 5, "apples")
            return regular_view(request, "logging")

        self._get_response = view
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        records = self.panel.get_stats()["records"]

        self.assertEqual(1, len(records))
        self.assertEqual("There are 5 apples", records[0]["message"])

    def test_insert_content(self):
        """
        Test that the panel only inserts content after generate_stats and
        not the process_request.
        """

        def view(request):
            self.logger.info("café")
            return regular_view(request, "logging")

        self._get_response = view
        response = self.panel.process_request(self.request)
        # ensure the panel does not have content yet.
        self.assertNotIn("café", self.panel.content)
        self.panel.generate_stats(self.request, response)
        # ensure the panel renders correctly.
        self.assertIn("café", self.panel.content)
        self.assertValidHTML(self.panel.content)

    def test_failing_formatting(self):
        class BadClass:
            def __str__(self):
                raise Exception("Please not stringify me!")

        def view(request):
            # should not raise exception, but fail silently
            self.logger.debug("This class is misbehaving: %s", BadClass())
            return regular_view(request, "logging")

        self._get_response = view
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        records = self.panel.get_stats()["records"]

        self.assertEqual(1, len(records))
        self.assertEqual(
            MESSAGE_IF_STRING_REPRESENTATION_INVALID, records[0]["message"]
        )
