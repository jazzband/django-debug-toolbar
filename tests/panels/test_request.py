from django.http import QueryDict

from ..base import BaseTestCase


class RequestPanelTestCase(BaseTestCase):
    panel_id = "RequestPanel"

    def test_non_ascii_session(self):
        self.request.session = {"où": "où"}
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        self.assertIn("où", self.panel.content)

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
        content = self.panel.content
        self.assertIn("nôt åscíì", content)
        self.assertValidHTML(content)

    def test_query_dict_for_request_in_method_get(self):
        """
        Test verifies the correctness of the statistics generation method
        in the case when the GET request is class QueryDict
        """
        self.request.GET = QueryDict("foo=bar")
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        # ensure the panel GET request data is processed correctly.
        content = self.panel.content
        self.assertIn("foo", content)
        self.assertIn("bar", content)

    def test_dict_for_request_in_method_get(self):
        """
        Test verifies the correctness of the statistics generation method
        in the case when the GET request is class Dict
        """
        self.request.GET = {"foo": "bar"}
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        # ensure the panel GET request data is processed correctly.
        content = self.panel.content
        self.assertIn("foo", content)
        self.assertIn("bar", content)

    def test_query_dict_for_request_in_method_post(self):
        """
        Test verifies the correctness of the statistics generation method
        in the case when the POST request is class QueryDict
        """
        self.request.POST = QueryDict("foo=bar")
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        # ensure the panel POST request data is processed correctly.
        content = self.panel.content
        self.assertIn("foo", content)
        self.assertIn("bar", content)

    def test_dict_for_request_in_method_post(self):
        """
        Test verifies the correctness of the statistics generation method
        in the case when the POST request is class Dict
        """
        self.request.POST = {"foo": "bar"}
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        # ensure the panel POST request data is processed correctly.
        content = self.panel.content
        self.assertIn("foo", content)
        self.assertIn("bar", content)
