from time import perf_counter

import sqlparse
from django.core.management.commands.shell import Command
from django.db import connection

if connection.vendor == "postgresql":
    from django.db.backends.postgresql import base as base_module
else:
    from django.db.backends import utils as base_module

# 'debugsqlshell' is the same as the 'shell'.


# Command is required to exist to be loaded via
# django.core.managementload_command_class
__all__ = ["Command", "PrintQueryWrapper"]


class PrintQueryWrapper(base_module.CursorDebugWrapper):
    def execute(self, sql, params=()):
        start_time = perf_counter()
        try:
            return self.cursor.execute(sql, params)
        finally:
            raw_sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            end_time = perf_counter()
            duration = (end_time - start_time) * 1000
            formatted_sql = sqlparse.format(raw_sql, reindent=True)
            print(f"{formatted_sql} [{duration:.2f}ms]")


base_module.CursorDebugWrapper = PrintQueryWrapper
