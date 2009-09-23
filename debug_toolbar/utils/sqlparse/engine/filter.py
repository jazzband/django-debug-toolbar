# -*- coding: utf-8 -*-

from debug_toolbar.utils.sqlparse import tokens as T
from debug_toolbar.utils.sqlparse.engine.grouping import Statement, Token


class TokenFilter(object):

    def __init__(self, **options):
        self.options = options

    def process(self, stack, stream):
        """Process token stream."""
        raise NotImplementedError


class StatementFilter(TokenFilter):

    def __init__(self):
        TokenFilter.__init__(self)
        self._in_declare = False
        self._in_dbldollar = False
        self._is_create = False

    def _reset(self):
        self._in_declare = False
        self._in_dbldollar = False
        self._is_create = False

    def _change_splitlevel(self, ttype, value):
        # PostgreSQL
        if (ttype == T.Name.Builtin
            and value.startswith('$') and value.endswith('$')):
            if self._in_dbldollar:
                self._in_dbldollar = False
                return -1
            else:
                self._in_dbldollar = True
                return 1
        elif self._in_dbldollar:
            return 0

        # ANSI
        if ttype is not T.Keyword:
            return 0

        unified = value.upper()

        if unified == 'DECLARE':
            self._in_declare = True
            return 1

        if unified == 'BEGIN':
            if self._in_declare:
                return 0
            return 0

        if unified == 'END':
            # Should this respect a preceeding BEGIN?
            # In CASE ... WHEN ... END this results in a split level -1.
            return -1

        if ttype is T.Keyword.DDL and unified.startswith('CREATE'):
            self._is_create = True

        if unified in ('IF', 'FOR') and self._is_create:
            return 1

        # Default
        return 0

    def process(self, stack, stream):
        splitlevel = 0
        stmt = None
        consume_ws = False
        stmt_tokens = []
        for ttype, value in stream:
            # Before appending the token
            if (consume_ws and ttype is not T.Whitespace
                and ttype is not T.Comment.Single):
                consume_ws = False
                stmt.tokens = stmt_tokens
                yield stmt
                self._reset()
                stmt = None
                splitlevel = 0
            if stmt is None:
                stmt = Statement()
                stmt_tokens = []
            splitlevel += self._change_splitlevel(ttype, value)
            # Append the token
            stmt_tokens.append(Token(ttype, value))
            # After appending the token
            if (splitlevel <= 0 and ttype is T.Punctuation
                and value == ';'):
                consume_ws = True
        if stmt is not None:
            stmt.tokens = stmt_tokens
            yield stmt
