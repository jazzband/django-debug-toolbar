from unittest.mock import patch

from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from debug_toolbar.decorators import render_with_toolbar_language


@render_with_toolbar_language
def stub_view(request):
    return HttpResponse(200)


@override_settings(DEBUG=True, LANGUAGE_CODE="fr")
class RenderWithToolbarLanguageTestCase(TestCase):
    @override_settings(DEBUG_TOOLBAR_CONFIG={"TOOLBAR_LANGUAGE": "de"})
    @patch("debug_toolbar.decorators.language_override")
    def test_uses_toolbar_language(self, mock_language_override):
        stub_view(RequestFactory().get("/"))
        mock_language_override.assert_called_once_with("de")

    @patch("debug_toolbar.decorators.language_override")
    def test_defaults_to_django_language_code(self, mock_language_override):
        stub_view(RequestFactory().get("/"))
        mock_language_override.assert_called_once_with("fr")
