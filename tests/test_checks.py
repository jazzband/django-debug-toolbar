import os
import unittest

import django
from django.conf import settings
from django.core.checks import Warning, run_checks
from django.test import SimpleTestCase, override_settings

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
