import os
from optparse import make_option

from django.db.backends import util
from django.core.management.commands.shell import Command

from debug_toolbar.utils import sqlparse

class PrintQueryWrapper(util.CursorDebugWrapper):
    def execute(self, sql, params=()):
        try:
            return self.cursor.execute(sql, params)
        finally:
            raw_sql = self.db.ops.last_executed_query(self.cursor, sql, params)
            print sqlparse.format(raw_sql, reindent=True)
            print

util.CursorDebugWrapper = PrintQueryWrapper
