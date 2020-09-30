from django.core.checks import Warning, run_checks
from django.test import SimpleTestCase, override_settings


class ChecksTestCase(SimpleTestCase):
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
