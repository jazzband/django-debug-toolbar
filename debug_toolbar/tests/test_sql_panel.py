from mock import patch, Mock

from django.test import TestCase
from django.utils.encoding import DjangoUnicodeDecodeError

from debug_toolbar.panels.sql import DatabaseStatTracker

class DatabaseStatTrackerTests(TestCase):

    def setUp(self):
        self.tracker = DatabaseStatTracker(Mock(), Mock())
        self.tracker.db.queries = []

    @patch('debug_toolbar.panels.sql.force_unicode')
    def test_execute_gracefully_handles_nonunicode_params(self, force_unicode):
        force_unicode.side_effect = DjangoUnicodeDecodeError("", "", "", 1, 1, "")
        self.tracker.execute('some sql', ('param1', ))
        self.assertEqual('["<non unicode object>"]', self.tracker.db.queries[0]['params'])

    @patch('debug_toolbar.panels.sql.simplejson.dumps')
    def test_execute_gracefully_handles_non_json_serializable_objects(self, dumps):
        dumps.side_effect = TypeError('not jsonable')
        self.tracker.execute('some sql', ('param1', ))
        self.assertEqual('', self.tracker.db.queries[0]['params'])