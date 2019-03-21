from ..base import BaseTestCase


class RequestPanelTestCase(BaseTestCase):
    panel_id = "RequestPanel"

    def test_non_ascii_session(self):
        self.request.session = {"où": "où"}
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        content = self.panel.content
        self.assertIn("où", content)

    def test_object_with_non_ascii_repr_in_request_params(self):
        self.request.path = "/non_ascii_request/"
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        self.assertIn("nôt åscíì", self.panel.content)

    def test_insert_content(self):
        """
        Test that the panel only inserts content after generate_stats and
        not the process_request.
        """
        self.request.path = "/non_ascii_request/"
        response = self.panel.process_request(self.request)
        # ensure the panel does not have content yet.
        self.assertNotIn("nôt åscíì", self.panel.content)
        self.panel.generate_stats(self.request, response)
        # ensure the panel renders correctly.
        self.assertIn("nôt åscíì", self.panel.content)
        self.assertValidHTML(self.panel.content)
