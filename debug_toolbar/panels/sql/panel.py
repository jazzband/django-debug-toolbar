import json
import uuid
from collections import defaultdict
from copy import copy
from pprint import saferepr

from django.db import connections
from django.urls import path
from django.utils.translation import gettext_lazy as _, ngettext

from debug_toolbar import settings as dt_settings
from debug_toolbar.forms import SignedDataForm
from debug_toolbar.panels import Panel
from debug_toolbar.panels.sql import views
from debug_toolbar.panels.sql.forms import SQLSelectForm
from debug_toolbar.panels.sql.tracking import unwrap_cursor, wrap_cursor
from debug_toolbar.panels.sql.utils import (
    contrasting_color_generator,
    decode_param,
    reformat_sql,
)
from debug_toolbar.utils import render_stacktrace


def get_isolation_level_display(vendor, level):
    if vendor == "postgresql":
        import psycopg2.extensions

        choices = {
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT: _("Autocommit"),
            psycopg2.extensions.ISOLATION_LEVEL_READ_UNCOMMITTED: _("Read uncommitted"),
            psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED: _("Read committed"),
            psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ: _("Repeatable read"),
            psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE: _("Serializable"),
        }
    else:
        raise ValueError(vendor)
    return choices.get(level)


def get_transaction_status_display(vendor, level):
    if vendor == "postgresql":
        import psycopg2.extensions

        choices = {
            psycopg2.extensions.TRANSACTION_STATUS_IDLE: _("Idle"),
            psycopg2.extensions.TRANSACTION_STATUS_ACTIVE: _("Active"),
            psycopg2.extensions.TRANSACTION_STATUS_INTRANS: _("In transaction"),
            psycopg2.extensions.TRANSACTION_STATUS_INERROR: _("In error"),
            psycopg2.extensions.TRANSACTION_STATUS_UNKNOWN: _("Unknown"),
        }
    else:
        raise ValueError(vendor)
    return choices.get(level)


class SQLPanel(Panel):
    """
    Panel that displays information about the SQL queries run while processing
    the request.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._offset = {k: len(connections[k].queries) for k in connections}
        self._sql_time = 0
        self._num_queries = 0
        self._queries = []
        self._databases = {}
        self._transaction_status = {}
        self._transaction_ids = {}

    def get_transaction_id(self, alias):
        if alias not in connections:
            return
        conn = connections[alias].connection
        if not conn:
            return

        if conn.vendor == "postgresql":
            cur_status = conn.get_transaction_status()
        else:
            raise ValueError(conn.vendor)

        last_status = self._transaction_status.get(alias)
        self._transaction_status[alias] = cur_status

        if not cur_status:
            # No available state
            return None

        if cur_status != last_status:
            if cur_status:
                self._transaction_ids[alias] = uuid.uuid4().hex
            else:
                self._transaction_ids[alias] = None

        return self._transaction_ids[alias]

    def record(self, alias, **kwargs):
        self._queries.append((alias, kwargs))
        if alias not in self._databases:
            self._databases[alias] = {
                "time_spent": kwargs["duration"],
                "num_queries": 1,
            }
        else:
            self._databases[alias]["time_spent"] += kwargs["duration"]
            self._databases[alias]["num_queries"] += 1
        self._sql_time += kwargs["duration"]
        self._num_queries += 1

    # Implement the Panel API

    nav_title = _("SQL")

    @property
    def nav_subtitle(self):
        return ngettext(
            "%(query_count)d query in %(sql_time).2fms",
            "%(query_count)d queries in %(sql_time).2fms",
            self._num_queries,
        ) % {
            "query_count": self._num_queries,
            "sql_time": self._sql_time,
        }

    @property
    def title(self):
        count = len(self._databases)
        return ngettext(
            "SQL queries from %(count)d connection",
            "SQL queries from %(count)d connections",
            count,
        ) % {"count": count}

    template = "debug_toolbar/panels/sql.html"

    @property
    def content(self):
        if not self.get_stats():
            self.record_stats(self.get_context())
        return super().content

    @classmethod
    def get_urls(cls):
        return [
            path("sql_select/", views.sql_select, name="sql_select"),
            path("sql_explain/", views.sql_explain, name="sql_explain"),
            path("sql_profile/", views.sql_profile, name="sql_profile"),
        ]

    def enable_instrumentation(self):
        # This is thread-safe because database connections are thread-local.
        for connection in connections.all():
            wrap_cursor(connection, self)

    def disable_instrumentation(self):
        for connection in connections.all():
            unwrap_cursor(connection)

    def get_context(self):
        queries = []

        colors = contrasting_color_generator()
        trace_colors = defaultdict(lambda: next(colors))
        query_similar = defaultdict(lambda: defaultdict(int))
        query_duplicates = defaultdict(lambda: defaultdict(int))

        # The keys used to determine similar and duplicate queries.
        def similar_key(query):
            return query["raw_sql"]

        def duplicate_key(query):
            raw_params = (
                () if query["raw_params"] is None else tuple(query["raw_params"])
            )
            # saferepr() avoids problems because of unhashable types
            # (e.g. lists) when used as dictionary keys.
            # https://github.com/jazzband/django-debug-toolbar/issues/1091
            return (query["raw_sql"], saferepr(raw_params))

        if self._queries:
            sql_warning_threshold = dt_settings.get_config()["SQL_WARNING_THRESHOLD"]
            width_ratio_tally = 0
            factor = int(256.0 / (len(self._databases) * 2.5))
            for n, db in enumerate(self._databases.values()):
                rgb = [0, 0, 0]
                color = n % 3
                rgb[color] = 256 - n // 3 * factor
                nn = color
                # XXX: pretty sure this is horrible after so many aliases
                while rgb[color] < factor:
                    nc = min(256 - rgb[color], 256)
                    rgb[color] += nc
                    nn += 1
                    if nn > 2:
                        nn = 0
                    rgb[nn] = nc
                db["rgb_color"] = rgb

            trans_ids = {}
            trans_id = None
            for alias, recorded_query in self._queries:
                query = dict(recorded_query)

                try:
                    params = json.dumps(decode_param(query["raw_params"]))
                except TypeError:
                    # object not JSON serializable
                    params = ""
                query["params"] = params

                query_similar[alias][similar_key(query)] += 1
                query_duplicates[alias][duplicate_key(query)] += 1

                trans_id = query.get("trans_id")
                last_trans_id = trans_ids.get(alias)

                if trans_id != last_trans_id:
                    if last_trans_id:
                        queries[-1]["ends_trans"] = True
                    trans_ids[alias] = trans_id
                    if trans_id:
                        query["starts_trans"] = True
                if trans_id:
                    query["in_trans"] = True

                query["alias"] = alias
                if "iso_level" in query:
                    query["iso_level"] = get_isolation_level_display(
                        query["vendor"], query["iso_level"]
                    )
                if "trans_status" in query:
                    query["trans_status"] = get_transaction_status_display(
                        query["vendor"], query["trans_status"]
                    )

                query["form"] = SignedDataForm(
                    auto_id=None, initial=SQLSelectForm(initial=copy(query)).initial
                )

                query["is_slow"] = query["duration"] > sql_warning_threshold
                query["is_select"] = (
                    query["raw_sql"].lower().lstrip().startswith("select")
                )

                if query["sql"]:
                    query["sql"] = reformat_sql(query["sql"], with_toggle=True)
                query["rgb_color"] = self._databases[alias]["rgb_color"]
                try:
                    query["width_ratio"] = (query["duration"] / self._sql_time) * 100
                except ZeroDivisionError:
                    query["width_ratio"] = 0
                query["start_offset"] = width_ratio_tally
                query["end_offset"] = query["width_ratio"] + query["start_offset"]
                width_ratio_tally += query["width_ratio"]
                query["stacktrace"] = render_stacktrace(query["stacktrace"])

                query["trace_color"] = trace_colors[query["stacktrace"]]

                queries.append(query)

            if trans_id:
                queries[-1]["ends_trans"] = True

        # Queries are similar / duplicates only if there's as least 2 of them.
        # Also, to hide queries, we need to give all the duplicate groups an id
        query_colors = contrasting_color_generator()
        query_similar_colors = {
            alias: {
                query: (similar_count, next(query_colors))
                for query, similar_count in queries.items()
                if similar_count >= 2
            }
            for alias, queries in query_similar.items()
        }
        query_duplicates_colors = {
            alias: {
                query: (duplicate_count, next(query_colors))
                for query, duplicate_count in queries.items()
                if duplicate_count >= 2
            }
            for alias, queries in query_duplicates.items()
        }

        for query in queries:
            alias = query["alias"]
            try:
                (query["similar_count"], query["similar_color"]) = query_similar_colors[
                    alias
                ][similar_key(query)]
                (
                    query["duplicate_count"],
                    query["duplicate_color"],
                ) = query_duplicates_colors[alias][duplicate_key(query)]
            except KeyError:
                pass

        for alias, alias_info in self._databases.items():
            try:
                alias_info["similar_count"] = sum(
                    e[0] for e in query_similar_colors[alias].values()
                )
                alias_info["duplicate_count"] = sum(
                    e[0] for e in query_duplicates_colors[alias].values()
                )
            except KeyError:
                pass

        return {
            "databases": sorted(
                self._databases.items(), key=lambda x: -x[1]["time_spent"]
            ),
            "queries": queries,
            "sql_time": self._sql_time,
        }

    def generate_server_timing(self, request, response):
        title = f"SQL {len(self._queries)} queries"
        self.record_server_timing("sql_time", title, self._sql_time)
