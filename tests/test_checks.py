import os
import sys
import unittest
from unittest.mock import patch

import django
from django.conf import settings
from django.core.checks import Error, Warning, run_checks
from django.test import SimpleTestCase, override_settings

from debug_toolbar import settings as dt_settings
from debug_toolbar.apps import debug_toolbar_installed_when_running_tests_check

PATH_DOES_NOT_EXIST = os.path.join(settings.BASE_DIR, "tests", "invalid_static")


class ChecksTestCase(SimpleTestCase):
    @override_settings(
        MIDDLEWARE=[
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.middleware.gzip.GZipMiddleware",
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ]
    )
    def test_check_good_configuration(self):
        messages = run_checks()
        self.assertEqual(messages, [])

    @override_settings(
        MIDDLEWARE=[
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ]
    )
    def test_check_missing_middleware_error(self):
        messages = run_checks()
        self.assertEqual(
            messages,
            [
                Warning(
                    "debug_toolbar.middleware.DebugToolbarMiddleware is "
                    "missing from MIDDLEWARE.",
                    hint="Add debug_toolbar.middleware.DebugToolbarMiddleware "
                    "to MIDDLEWARE.",
                    id="debug_toolbar.W001",
                )
            ],
        )

    @override_settings(
        MIDDLEWARE=[
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "debug_toolbar.middleware.DebugToolbarMiddleware",
            "django.middleware.gzip.GZipMiddleware",
        ]
    )
    def test_check_gzip_middleware_error(self):
        messages = run_checks()
        self.assertEqual(
            messages,
            [
                Warning(
                    "debug_toolbar.middleware.DebugToolbarMiddleware occurs "
                    "before django.middleware.gzip.GZipMiddleware in "
                    "MIDDLEWARE.",
                    hint="Move debug_toolbar.middleware.DebugToolbarMiddleware "
                    "to after django.middleware.gzip.GZipMiddleware in "
                    "MIDDLEWARE.",
                    id="debug_toolbar.W003",
                )
            ],
        )

    @override_settings(
        MIDDLEWARE_CLASSES=[
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.middleware.gzip.GZipMiddleware",
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ]
    )
    def test_check_middleware_classes_error(self):
        messages = run_checks()
        self.assertIn(
            Warning(
                "debug_toolbar is incompatible with MIDDLEWARE_CLASSES setting.",
                hint="Use MIDDLEWARE instead of MIDDLEWARE_CLASSES",
                id="debug_toolbar.W004",
            ),
            messages,
        )

    @unittest.skipIf(django.VERSION >= (4,), "Django>=4 handles missing dirs itself.")
    @override_settings(
        STATICFILES_DIRS=[PATH_DOES_NOT_EXIST],
    )
    def test_panel_check_errors(self):
        messages = run_checks()
        self.assertEqual(
            messages,
            [
                Warning(
                    "debug_toolbar requires the STATICFILES_DIRS directories to exist.",
                    hint="Running manage.py collectstatic may help uncover the issue.",
                    id="debug_toolbar.staticfiles.W001",
                )
            ],
        )

    @override_settings(DEBUG_TOOLBAR_PANELS=[])
    def test_panels_is_empty(self):
        errors = run_checks()
        self.assertEqual(
            errors,
            [
                Warning(
                    "Setting DEBUG_TOOLBAR_PANELS is empty.",
                    hint="Set DEBUG_TOOLBAR_PANELS to a non-empty list in your "
                    "settings.py.",
                    id="debug_toolbar.W005",
                )
            ],
        )

    @override_settings(
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": False,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                    "loaders": [
                        "django.template.loaders.filesystem.Loader",
                    ],
                },
            },
        ]
    )
    def test_check_w006_invalid(self):
        errors = run_checks()
        self.assertEqual(
            errors,
            [
                Warning(
                    "At least one DjangoTemplates TEMPLATES configuration needs "
                    "to use django.template.loaders.app_directories.Loader or "
                    "have APP_DIRS set to True.",
                    hint=(
                        "Include django.template.loaders.app_directories.Loader "
                        'in ["OPTIONS"]["loaders"]. Alternatively use '
                        "APP_DIRS=True for at least one "
                        "django.template.backends.django.DjangoTemplates "
                        "backend configuration."
                    ),
                    id="debug_toolbar.W006",
                )
            ],
        )

    @override_settings(
        TEMPLATES=[
            {
                "NAME": "use_loaders",
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": False,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                    "loaders": [
                        "django.template.loaders.app_directories.Loader",
                    ],
                },
            },
            {
                "NAME": "use_app_dirs",
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            },
        ]
    )
    def test_check_w006_valid(self):
        self.assertEqual(run_checks(), [])

    @override_settings(
        TEMPLATES=[
            {
                "NAME": "use_loaders",
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": False,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                    "loaders": [
                        (
                            "django.template.loaders.cached.Loader",
                            [
                                "django.template.loaders.filesystem.Loader",
                                "django.template.loaders.app_directories.Loader",
                            ],
                        ),
                    ],
                },
            },
        ]
    )
    def test_check_w006_valid_nested_loaders(self):
        self.assertEqual(run_checks(), [])

    @patch("debug_toolbar.apps.mimetypes.guess_type")
    def test_check_w007_valid(self, mocked_guess_type):
        mocked_guess_type.return_value = ("text/javascript", None)
        self.assertEqual(run_checks(), [])
        mocked_guess_type.return_value = ("application/javascript", None)
        self.assertEqual(run_checks(), [])

    @patch("debug_toolbar.apps.mimetypes.guess_type")
    def test_check_w007_invalid(self, mocked_guess_type):
        mocked_guess_type.return_value = ("text/plain", None)
        self.assertEqual(
            run_checks(),
            [
                Warning(
                    "JavaScript files are resolving to the wrong content type.",
                    hint="The Django Debug Toolbar may not load properly while mimetypes are misconfigured. "
                    "See the Django documentation for an explanation of why this occurs.\n"
                    "https://docs.djangoproject.com/en/stable/ref/contrib/staticfiles/#static-file-development-view\n"
                    "\n"
                    "This typically occurs on Windows machines. The suggested solution is to modify "
                    "HKEY_CLASSES_ROOT in the registry to specify the content type for JavaScript "
                    "files.\n"
                    "\n"
                    "[HKEY_CLASSES_ROOT\\.js]\n"
                    '"Content Type"="application/javascript"',
                    id="debug_toolbar.W007",
                )
            ],
        )


def test_check_w008_valid(self):
    settings.DEBUG = True
    dt_settings.get_config()["RUNNING_TESTS"] = "test"
    errors = debug_toolbar_installed_when_running_tests_check(None)
    self.assertEqual(
        errors,
        [
            Error(
                "debug toolbar is not a registered namespace",
                hint="The Django Debug Toolbar is misconfigured, check the documentation for proper configuration when running tests",
                id="debug_toolbar.W008",
            )
        ],
    )

    @patch("debug_toolbar.apps.debug_toolbar_installed_when_running_tests_check", [])
    def test_debug_toolbar_installed_when_running_tests_check_with_debug_false(
        self, mocked_get_config
    ):
        mocked_get_config.return_value = {"RUNNING_TESTS": "not_test"}
        settings.DEBUG = False
        errors = debug_toolbar_installed_when_running_tests_check(None)
        self.assertEqual(len(errors), 0)

    @patch("debug_toolbar.apps.debug_toolbar_installed_when_running_tests_check", [])
    def test_debug_toolbar_installed_when_running_tests_check_with_debug_true(
        self, mocked_get_config
    ):
        mocked_get_config.return_value = {"RUNNING_TESTS": "test"}
        settings.DEBUG = True
        sys.argv = ["manage.py", "test"]
        errors = debug_toolbar_installed_when_running_tests_check(None)
        self.assertEqual(len(errors), 0)

    @patch("debug_toolbar.apps.debug_toolbar_installed_when_running_tests_check", [])
    def test_debug_toolbar_installed_when_running_tests_check_with_running_tests_not_test(
        self, mock_get_config
    ):
        mock_get_config.return_value = {"RUNNING_TESTS": "not_test"}
        settings.DEBUG = True
        sys.argv = ["manage.py", "test"]
        errors = debug_toolbar_installed_when_running_tests_check(None)
        self.assertEqual(len(errors), 0)

    @patch("debug_toolbar.apps.debug_toolbar_installed_when_running_tests_check", [])
    def test_debug_toolbar_installed_when_running_tests_check_with_debug_false_and_running_tests(
        self, mock_get_config
    ):
        mock_get_config.return_value = {"RUNNING_TESTS": "test"}
        settings.DEBUG = False
        errors = debug_toolbar_installed_when_running_tests_check(None)
        self.assertEqual(
            errors,
            [
                Error(
                    "django debug toolbar  is not a registered namespace ",
                    hint="The Django Debug Toolbar is misconfigured, check the documentation for proper configuration and run the tests.",
                    id="debug_toolbar.W008",
                )
            ],
        )
