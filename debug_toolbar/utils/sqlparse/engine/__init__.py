# Copyright (C) 2008 Andi Albrecht, albrecht.andi@gmail.com
#
# This module is part of python-sqlparse and is released under
# the BSD License: http://www.opensource.org/licenses/bsd-license.php.

"""filter"""

import re

from debug_toolbar.utils.sqlparse import lexer, SQLParseError
from debug_toolbar.utils.sqlparse.engine import grouping
from debug_toolbar.utils.sqlparse.engine.filter import StatementFilter

# XXX remove this when cleanup is complete
Filter = object


class FilterStack(object):

    def __init__(self):
        self.preprocess = []
        self.stmtprocess = []
        self.postprocess = []
        self.split_statements = False
        self._grouping = False

    def _flatten(self, stream):
        for token in stream:
            if token.is_group():
                for t in self._flatten(token.tokens):
                    yield t
            else:
                yield token

    def enable_grouping(self):
        self._grouping = True

    def full_analyze(self):
        self.enable_grouping()

    def run(self, sql):
        stream = lexer.tokenize(sql)
        # Process token stream
        if self.preprocess:
           for filter_ in self.preprocess:
               stream = filter_.process(self, stream)

        if (self.stmtprocess or self.postprocess or self.split_statements
            or self._grouping):
            splitter = StatementFilter()
            stream = splitter.process(self, stream)

        if self._grouping:
            def _group(stream):
                for stmt in stream:
                    grouping.group(stmt)
                    yield stmt
            stream = _group(stream)

        if self.stmtprocess:
            def _run(stream):
                ret = []
                for stmt in stream:
                    for filter_ in self.stmtprocess:
                        filter_.process(self, stmt)
                    ret.append(stmt)
                return ret
            stream = _run(stream)

        if self.postprocess:
            def _run(stream):
                for stmt in stream:
                    stmt.tokens = list(self._flatten(stmt.tokens))
                    for filter_ in self.postprocess:
                        stmt = filter_.process(self, stmt)
                    yield stmt
            stream = _run(stream)

        return stream

