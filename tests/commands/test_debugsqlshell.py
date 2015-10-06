from __future__ import absolute_import, unicode_literals

import sys

from django.contrib.auth.models import User
from django.core import management
from django.db.backends import utils as db_backends_utils
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import six


@override_settings(DEBUG=True)
class DebugSQLShellTestCase(TestCase):

    def setUp(self):
        self.original_cursor_wrapper = db_backends_utils.CursorDebugWrapper
        # Since debugsqlshell monkey-patches django.db.backends.utils, we can
        # test it simply by loading it, without executing it. But we have to
        # undo the monkey-patch on exit.
        command_name = 'debugsqlshell'
        app_name = management.get_commands()[command_name]
        management.load_command_class(app_name, command_name)

    def tearDown(self):
        db_backends_utils.CursorDebugWrapper = self.original_cursor_wrapper

    def test_command(self):
        original_stdout, sys.stdout = sys.stdout, six.StringIO()
        try:
            User.objects.count()
            self.assertIn("SELECT COUNT", sys.stdout.getvalue())
        finally:
            sys.stdout = original_stdout
