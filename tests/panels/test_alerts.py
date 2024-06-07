from django.http import HttpResponse
from django.template import Context, Template

from ..base import BaseTestCase


class AlertsPanelTestCase(BaseTestCase):
    panel_id = "AlertsPanel"

    def test_issue_warning_display(self):
        """
        Test that the panel (does not) display[s] a warning when there are
        (no) issues.
        """
        self.panel.issues = 0
        nav_subtitle = self.panel.nav_subtitle
        self.assertNotIn("issues found", nav_subtitle)

        self.panel.issues = ["Issue 1", "Issue 2"]
        nav_subtitle = self.panel.nav_subtitle
        self.assertIn("2 issues found", nav_subtitle)

    def test_file_form_without_enctype_multipart_form_data(self):
        """
        Test that the panel displays a form invalid message when there is
        a file input but encoding not set to multipart/form-data.
        """
        test_form = '<form id="test-form"><input type="file"></form>'
        result = self.panel.check_invalid_file_form_configuration(test_form)
        expected_error = (
            'Form with id "test-form" contains file input '
            "but does not have multipart/form-data encoding."
        )
        self.assertEqual(result[0]["issue"], expected_error)
        self.assertEqual(len(result), 1)

    def test_file_form_with_enctype_multipart_form_data(self):
        test_form = """<form id="test-form" enctype="multipart/form-data">
        <input type="file">
        </form>"""
        result = self.panel.check_invalid_file_form_configuration(test_form)

        self.assertEqual(len(result), 0)

    def test_integration_file_form_without_enctype_multipart_form_data(self):
        t = Template('<form id="test-form"><input type="file"></form>')
        c = Context({})
        rendered_template = t.render(c)
        response = HttpResponse(content=rendered_template)

        self.panel.generate_stats(self.request, response)

        self.assertIn(
            "Form with id &quot;test-form&quot; contains file input "
            "but does not have multipart/form-data encoding.",
            self.panel.content,
        )
