# Add tests to example app to check how the toolbar is used
# when running tests for a project.
# See https://github.com/jazzband/django-debug-toolbar/issues/1405

from django.test import TestCase
from django.urls import reverse


class ViewTestCase(TestCase):
    def test_index(self):
        response = self.client.get(reverse("home"))
        assert response.status_code == 200
