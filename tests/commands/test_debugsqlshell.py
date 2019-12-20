import io
import sys

from django.contrib.auth.models import User
from django.core import management
from django.db import connection
from django.test import TestCase
from django.test.utils import override_settings

if connection.vendor == "postgresql":
    from django.db.backends.postgresql import base as base_module
else:
    from django.db.backends import utils as base_module


@override_settings(DEBUG=True)
class DebugSQLShellTestCase(TestCase):
    def setUp(self):
        self.original_wrapper = base_module.CursorDebugWrapper
        # Since debugsqlshell monkey-patches django.db.backends.utils, we can
        # test it simply by loading it, without executing it. But we have to
        # undo the monkey-patch on exit.
        command_name = "debugsqlshell"
        app_name = management.get_commands()[command_name]
        management.load_command_class(app_name, command_name)

    def tearDown(self):
        base_module.CursorDebugWrapper = self.original_wrapper

    def test_command(self):
        original_stdout, sys.stdout = sys.stdout, io.StringIO()
        try:
            User.objects.count()
            self.assertIn("SELECT COUNT", sys.stdout.getvalue())
        finally:
            sys.stdout = original_stdout
