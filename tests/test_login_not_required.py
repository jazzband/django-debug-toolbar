import unittest

import django
from django.test import SimpleTestCase, override_settings
from django.urls import reverse


@unittest.skipIf(
    django.VERSION < (5, 1),
    "Valid on Django 5.1 and above, requires LoginRequiredMiddleware",
)
@override_settings(
    DEBUG=True,
    MIDDLEWARE=[
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.auth.middleware.LoginRequiredMiddleware",
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ],
)
class LoginNotRequiredTestCase(SimpleTestCase):
    def test_panels(self):
        for uri in (
            "history_sidebar",
            "history_refresh",
            "sql_select",
            "sql_explain",
            "sql_profile",
            "template_source",
        ):
            with self.subTest(uri=uri):
                response = self.client.get(reverse(f"djdt:{uri}"))
                self.assertNotEqual(response.status_code, 200)

    def test_render_panel(self):
        response = self.client.get(
            reverse("djdt:render_panel"), query_params={"store_id": "store_id"}
        )
        self.assertEqual(response.status_code, 200)
