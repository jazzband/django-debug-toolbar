from unittest.mock import patch

from django.core.checks import Warning, run_checks
from django.test import SimpleTestCase, override_settings
from django.urls import NoReverseMatch

from debug_toolbar.apps import debug_toolbar_installed_when_running_tests_check


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
                ),
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

    @patch("debug_toolbar.apps.reverse")
    def test_debug_toolbar_installed_when_running_tests(self, reverse):
        params = [
            {
                "debug": True,
                "running_tests": True,
                "show_callback_changed": True,
                "urls_installed": False,
                "errors": False,
            },
            {
                "debug": False,
                "running_tests": False,
                "show_callback_changed": True,
                "urls_installed": False,
                "errors": False,
            },
            {
                "debug": False,
                "running_tests": True,
                "show_callback_changed": False,
                "urls_installed": False,
                "errors": False,
            },
            {
                "debug": False,
                "running_tests": True,
                "show_callback_changed": True,
                "urls_installed": True,
                "errors": False,
            },
            {
                "debug": False,
                "running_tests": True,
                "show_callback_changed": True,
                "urls_installed": False,
                "errors": True,
            },
        ]
        for config in params:
            with self.subTest(**config):
                config_setting = {
                    "RENDER_PANELS": False,
                    "IS_RUNNING_TESTS": config["running_tests"],
                    "SHOW_TOOLBAR_CALLBACK": (
                        (lambda *args: True)
                        if config["show_callback_changed"]
                        else "debug_toolbar.middleware.show_toolbar"
                    ),
                }
                if config["urls_installed"]:
                    reverse.side_effect = lambda *args: None
                else:
                    reverse.side_effect = NoReverseMatch()

                with self.settings(
                    DEBUG=config["debug"], DEBUG_TOOLBAR_CONFIG=config_setting
                ):
                    errors = debug_toolbar_installed_when_running_tests_check(None)
                    if config["errors"]:
                        self.assertEqual(len(errors), 1)
                        self.assertEqual(errors[0].id, "debug_toolbar.E001")
                    else:
                        self.assertEqual(len(errors), 0)

    @override_settings(
        DEBUG_TOOLBAR_CONFIG={
            "OBSERVE_REQUEST_CALLBACK": lambda request: False,
            "IS_RUNNING_TESTS": False,
        }
    )
    def test_observe_request_callback_specified(self):
        errors = run_checks()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].id, "debug_toolbar.W008")
