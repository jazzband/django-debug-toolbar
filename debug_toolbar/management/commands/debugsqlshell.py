from time import time

import django
import sqlparse
from django.core.management.commands.shell import Command  # noqa
from django.db import connection

if connection.vendor == "postgresql" and django.VERSION >= (3, 0, 0):
    from django.db.backends.postgresql import base as base_module
else:
    from django.db.backends import utils as base_module

# 'debugsqlshell' is the same as the 'shell'.


class PrintQueryWrapper(base_module.CursorDebugWrapper):
    def execute(self, sql, params=()):
        start_time = time()
        try:
            return self.cursor.execute(sql, params)
        finally:
            raw_sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            end_time = time()
            duration = (end_time - start_time) * 1000
            formatted_sql = sqlparse.format(raw_sql, reindent=True)
            print("{} [{:.2f}ms]".format(formatted_sql, duration))


base_module.CursorDebugWrapper = PrintQueryWrapper
