from __future__ import print_function

from datetime import datetime

from django.db.backends import util

import sqlparse

from debug_toolbar.utils import ms_from_timedelta


class PrintQueryWrapper(util.CursorDebugWrapper):
    def execute(self, sql, params=()):
        starttime = datetime.now()
        try:
            return self.cursor.execute(sql, params)
        finally:
            raw_sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            execution_time = ms_from_timedelta(datetime.now() - starttime)
            formatted_sql = sqlparse.format(raw_sql, reindent=True)
            print('%s [%.2fms]' % (formatted_sql, execution_time))


util.CursorDebugWrapper = PrintQueryWrapper
