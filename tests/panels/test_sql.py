import datetime
import unittest

import django
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count
from django.db.utils import DatabaseError
from django.shortcuts import render
from django.test.utils import override_settings

from ..base import BaseTestCase

try:
    from psycopg2._json import Json as PostgresJson
except ImportError:
    PostgresJson = None

if connection.vendor == "postgresql":
    from ..models import PostgresJSON as PostgresJSONModel
else:
    PostgresJSONModel = None


class SQLPanelTestCase(BaseTestCase):
    panel_id = "SQLPanel"

    def test_disabled(self):
        config = {"DISABLE_PANELS": {"debug_toolbar.panels.sql.SQLPanel"}}
        self.assertTrue(self.panel.enabled)
        with self.settings(DEBUG_TOOLBAR_CONFIG=config):
            self.assertFalse(self.panel.enabled)

    def test_recording(self):
        self.assertEqual(len(self.panel._queries), 0)

        list(User.objects.all())

        # ensure query was logged
        self.assertEqual(len(self.panel._queries), 1)
        query = self.panel._queries[0]
        self.assertEqual(query[0], "default")
        self.assertTrue("sql" in query[1])
        self.assertTrue("duration" in query[1])
        self.assertTrue("stacktrace" in query[1])

        # ensure the stacktrace is populated
        self.assertTrue(len(query[1]["stacktrace"]) > 0)

    @unittest.skipUnless(
        connection.vendor == "postgresql", "Test valid only on PostgreSQL"
    )
    def test_recording_chunked_cursor(self):
        self.assertEqual(len(self.panel._queries), 0)

        list(User.objects.all().iterator())

        # ensure query was logged
        self.assertEqual(len(self.panel._queries), 1)

    def test_generate_server_timing(self):
        self.assertEqual(len(self.panel._queries), 0)

        list(User.objects.all())

        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        self.panel.generate_server_timing(self.request, response)

        # ensure query was logged
        self.assertEqual(len(self.panel._queries), 1)
        query = self.panel._queries[0]

        expected_data = {
            "sql_time": {"title": "SQL 1 queries", "value": query[1]["duration"]}
        }

        self.assertEqual(self.panel.get_server_timing_stats(), expected_data)

    def test_non_ascii_query(self):
        self.assertEqual(len(self.panel._queries), 0)

        # non-ASCII text query
        list(User.objects.extra(where=["username = 'apéro'"]))
        self.assertEqual(len(self.panel._queries), 1)

        # non-ASCII text parameters
        list(User.objects.filter(username="thé"))
        self.assertEqual(len(self.panel._queries), 2)

        # non-ASCII bytes parameters
        list(User.objects.filter(username="café".encode()))
        self.assertEqual(len(self.panel._queries), 3)

        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)

        # ensure the panel renders correctly
        self.assertIn("café", self.panel.content)

    def test_param_conversion(self):
        self.assertEqual(len(self.panel._queries), 0)

        list(
            User.objects.filter(first_name="Foo")
            .filter(is_staff=True)
            .filter(is_superuser=False)
        )
        list(
            User.objects.annotate(group_count=Count("groups__id"))
            .filter(group_count__lt=10)
            .filter(group_count__gt=1)
        )
        list(User.objects.filter(date_joined=datetime.datetime(2017, 12, 22, 16, 7, 1)))

        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)

        # ensure query was logged
        self.assertEqual(len(self.panel._queries), 3)

        if django.VERSION >= (3, 1):
            self.assertEqual(
                tuple([q[1]["params"] for q in self.panel._queries]),
                ('["Foo"]', "[10, 1]", '["2017-12-22 16:07:01"]'),
            )
        else:
            self.assertEqual(
                tuple([q[1]["params"] for q in self.panel._queries]),
                ('["Foo", true, false]', "[10, 1]", '["2017-12-22 16:07:01"]'),
            )

    @unittest.skipUnless(
        connection.vendor == "postgresql", "Test valid only on PostgreSQL"
    )
    def test_json_param_conversion(self):
        self.assertEqual(len(self.panel._queries), 0)

        list(PostgresJSONModel.objects.filter(field__contains={"foo": "bar"}))

        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)

        # ensure query was logged
        self.assertEqual(len(self.panel._queries), 1)
        self.assertEqual(
            self.panel._queries[0][1]["params"], '["{\\"foo\\": \\"bar\\"}"]',
        )
        self.assertIsInstance(
            self.panel._queries[0][1]["raw_params"][0], PostgresJson,
        )

    def test_binary_param_force_text(self):
        self.assertEqual(len(self.panel._queries), 0)

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM tests_binary WHERE field = %s",
                [connection.Database.Binary(b"\xff")],
            )

        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)

        self.assertEqual(len(self.panel._queries), 1)
        self.assertIn(
            "<strong>SELECT</strong> * <strong>FROM</strong>"
            " tests_binary <strong>WHERE</strong> field =",
            self.panel._queries[0][1]["sql"],
        )

    @unittest.skipUnless(connection.vendor != "sqlite", "Test invalid for SQLite")
    def test_raw_query_param_conversion(self):
        self.assertEqual(len(self.panel._queries), 0)

        list(
            User.objects.raw(
                " ".join(
                    [
                        "SELECT *",
                        "FROM auth_user",
                        "WHERE first_name = %s",
                        "AND is_staff = %s",
                        "AND is_superuser = %s",
                        "AND date_joined = %s",
                    ]
                ),
                params=["Foo", True, False, datetime.datetime(2017, 12, 22, 16, 7, 1)],
            )
        )

        list(
            User.objects.raw(
                " ".join(
                    [
                        "SELECT *",
                        "FROM auth_user",
                        "WHERE first_name = %(first_name)s",
                        "AND is_staff = %(is_staff)s",
                        "AND is_superuser = %(is_superuser)s",
                        "AND date_joined = %(date_joined)s",
                    ]
                ),
                params={
                    "first_name": "Foo",
                    "is_staff": True,
                    "is_superuser": False,
                    "date_joined": datetime.datetime(2017, 12, 22, 16, 7, 1),
                },
            )
        )

        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)

        # ensure query was logged
        self.assertEqual(len(self.panel._queries), 2)

        self.assertEqual(
            tuple([q[1]["params"] for q in self.panel._queries]),
            (
                '["Foo", true, false, "2017-12-22 16:07:01"]',
                " ".join(
                    [
                        '{"first_name": "Foo",',
                        '"is_staff": true,',
                        '"is_superuser": false,',
                        '"date_joined": "2017-12-22 16:07:01"}',
                    ]
                ),
            ),
        )

    def test_insert_content(self):
        """
        Test that the panel only inserts content after generate_stats and
        not the process_request.
        """
        list(User.objects.filter(username="café".encode("utf-8")))
        response = self.panel.process_request(self.request)
        # ensure the panel does not have content yet.
        self.assertNotIn("café", self.panel.content)
        self.panel.generate_stats(self.request, response)
        # ensure the panel renders correctly.
        self.assertIn("café", self.panel.content)
        self.assertValidHTML(self.panel.content)

    @override_settings(DEBUG_TOOLBAR_CONFIG={"ENABLE_STACKTRACES_LOCALS": True})
    def test_insert_locals(self):
        """
        Test that the panel inserts locals() content.
        """
        local_var = "<script>alert('test');</script>"  # noqa
        list(User.objects.filter(username="café".encode("utf-8")))
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        self.assertIn("local_var", self.panel.content)
        # Verify the escape logic works
        self.assertNotIn("<script>alert", self.panel.content)
        self.assertIn("&lt;script&gt;alert", self.panel.content)
        self.assertIn("djdt-locals", self.panel.content)

    def test_not_insert_locals(self):
        """
        Test that the panel does not insert locals() content.
        """
        list(User.objects.filter(username="café".encode("utf-8")))
        response = self.panel.process_request(self.request)
        self.panel.generate_stats(self.request, response)
        self.assertNotIn("djdt-locals", self.panel.content)

    @unittest.skipUnless(
        connection.vendor == "postgresql", "Test valid only on PostgreSQL"
    )
    def test_erroneous_query(self):
        """
        Test that an error in the query isn't swallowed by the middleware.
        """
        try:
            connection.cursor().execute("erroneous query")
        except DatabaseError as e:
            self.assertTrue("erroneous query" in str(e))

    @unittest.skipUnless(
        connection.vendor == "postgresql", "Test valid only on PostgreSQL"
    )
    def test_execute_with_psycopg2_composed_sql(self):
        """
        Test command executed using a Composed psycopg2 object is logged.
        Ref: http://initd.org/psycopg/docs/sql.html
        """
        from psycopg2 import sql

        self.assertEqual(len(self.panel._queries), 0)

        with connection.cursor() as cursor:
            command = sql.SQL("select {field} from {table}").format(
                field=sql.Identifier("username"), table=sql.Identifier("auth_user")
            )
            cursor.execute(command)

        self.assertEqual(len(self.panel._queries), 1)

        query = self.panel._queries[0]
        self.assertEqual(query[0], "default")
        self.assertTrue("sql" in query[1])
        self.assertEqual(query[1]["sql"], 'select "username" from "auth_user"')

    def test_disable_stacktraces(self):
        self.assertEqual(len(self.panel._queries), 0)

        with self.settings(DEBUG_TOOLBAR_CONFIG={"ENABLE_STACKTRACES": False}):
            list(User.objects.all())

        # ensure query was logged
        self.assertEqual(len(self.panel._queries), 1)
        query = self.panel._queries[0]
        self.assertEqual(query[0], "default")
        self.assertTrue("sql" in query[1])
        self.assertTrue("duration" in query[1])
        self.assertTrue("stacktrace" in query[1])

        # ensure the stacktrace is empty
        self.assertEqual([], query[1]["stacktrace"])

    @override_settings(
        DEBUG=True,
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "OPTIONS": {"debug": True, "loaders": ["tests.loaders.LoaderWithSQL"]},
            }
        ],
    )
    def test_regression_infinite_recursion(self):
        """
        Test case for when the template loader runs a SQL query that causes
        an infinite recursion in the SQL panel.
        """
        self.assertEqual(len(self.panel._queries), 0)

        render(self.request, "basic.html", {})

        # Two queries are logged because the loader runs SQL every time a
        # template is loaded and basic.html extends base.html.
        self.assertEqual(len(self.panel._queries), 2)
        query = self.panel._queries[0]
        self.assertEqual(query[0], "default")
        self.assertTrue("sql" in query[1])
        self.assertTrue("duration" in query[1])
        self.assertTrue("stacktrace" in query[1])

        # ensure the stacktrace is populated
        self.assertTrue(len(query[1]["stacktrace"]) > 0)
