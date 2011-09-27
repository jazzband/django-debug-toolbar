from datetime import datetime

from django.db.backends import util
from django.core.management.commands.shell import Command

from debug_toolbar.utils import ms_from_timedelta, sqlparse


class PrintQueryWrapper(util.CursorDebugWrapper):
    def execute(self, sql, params=()):
        starttime = datetime.now()
        try:
            return self.cursor.execute(sql, params)
        finally:
            raw_sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            execution_time = datetime.now() - starttime
            print sqlparse.format(raw_sql, reindent=True),
            print ' [%.2fms]' % (ms_from_timedelta(execution_time),)
            print

util.CursorDebugWrapper = PrintQueryWrapper
