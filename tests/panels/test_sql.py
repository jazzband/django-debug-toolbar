# coding: utf-8

from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import connection
from django.db.utils import DatabaseError
from django.utils import unittest

from debug_toolbar.panels.sql import SQLDebugPanel

from ..base import BaseTestCase


class SQLPanelTestCase(BaseTestCase):

    def test_recording(self):
        panel = self.toolbar.get_panel(SQLDebugPanel)
        self.assertEqual(len(panel._queries), 0)

        list(User.objects.all())

        # ensure query was logged
        self.assertEqual(len(panel._queries), 1)
        query = panel._queries[0]
        self.assertEqual(query[0], 'default')
        self.assertTrue('sql' in query[1])
        self.assertTrue('duration' in query[1])
        self.assertTrue('stacktrace' in query[1])

        # ensure the stacktrace is populated
        self.assertTrue(len(query[1]['stacktrace']) > 0)

    def test_non_ascii_query(self):
        panel = self.toolbar.get_panel(SQLDebugPanel)
        self.assertEqual(len(panel._queries), 0)

        # non-ASCII query
        list(User.objects.extra(where=["username = 'café'"]))
        self.assertEqual(len(panel._queries), 1)

        # non-ASCII parameters
        list(User.objects.filter(username='café'))
        self.assertEqual(len(panel._queries), 2)

    @unittest.skipUnless(connection.vendor == 'postgresql',
                         'Test valid only on PostgreSQL')
    def test_erroneous_query(self):
        """
        Test that an error in the query isn't swallowed by the middleware.
        """
        try:
            connection.cursor().execute("erroneous query")
        except DatabaseError as e:
            self.assertTrue('erroneous query' in str(e))

    def test_disable_stacktraces(self):
        panel = self.toolbar.get_panel(SQLDebugPanel)
        self.assertEqual(len(panel._queries), 0)

        with self.settings(DEBUG_TOOLBAR_CONFIG={'ENABLE_STACKTRACES': False}):
            list(User.objects.all())

        # ensure query was logged
        self.assertEqual(len(panel._queries), 1)
        query = panel._queries[0]
        self.assertEqual(query[0], 'default')
        self.assertTrue('sql' in query[1])
        self.assertTrue('duration' in query[1])
        self.assertTrue('stacktrace' in query[1])

        # ensure the stacktrace is empty
        self.assertEqual([], query[1]['stacktrace'])
