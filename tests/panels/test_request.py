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

    def test_list_for_request_in_method_post(self):
        """
        Verify that the toolbar doesn't crash if request.POST contains unexpected data.

        See https://github.com/jazzband/django-debug-toolbar/issues/1621
        """
        self.request.POST = [{"a": 1}, {"b": 2}]
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        # ensure the panel POST request data is processed correctly.
        content = self.panel.content
        self.assertIn("[{&#x27;a&#x27;: 1}, {&#x27;b&#x27;: 2}]", content)

    def test_namespaced_url(self):
        self.request.path = "/admin/login/"
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        panel_stats = self.panel.get_stats()
        self.assertEqual(panel_stats["view_urlname"], "admin:login")

    def test_session_list_sorted_or_not(self):
        """
        Verify the session is sorted when all keys are strings.

        See  https://github.com/jazzband/django-debug-toolbar/issues/1668
        """
        self.request.session = {
            1: "value",
            "data": ["foo", "bar", 1],
            (2, 3): "tuple_key",
        }
        data = {
            "list": [(1, "value"), ("data", ["foo", "bar", 1]), ((2, 3), "tuple_key")]
        }
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        panel_stats = self.panel.get_stats()
        self.assertEqual(panel_stats["session"], data)

        self.request.session = {
            "b": "b-value",
            "a": "a-value",
        }
        data = {"list": [("a", "a-value"), ("b", "b-value")]}
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        panel_stats = self.panel.get_stats()
        self.assertEqual(panel_stats["session"], data)
