# -*- coding: utf-8 -*-

import re

from debug_toolbar.utils.sqlparse.engine import grouping
from debug_toolbar.utils.sqlparse import tokens as T
from debug_toolbar.utils.sqlparse import sql


class Filter(object):

    def process(self, *args):
        raise NotImplementedError


class TokenFilter(Filter):

    def process(self, stack, stream):
        raise NotImplementedError


# FIXME: Should be removed
def rstrip(stream):
    buff = []
    for token in stream:
        if token.is_whitespace() and '\n' in token.value:
            # assuming there's only one \n in value
            before, rest = token.value.split('\n', 1)
            token.value = '\n%s' % rest
            buff = []
            yield token
        elif token.is_whitespace():
            buff.append(token)
        elif token.is_group():
            token.tokens = list(rstrip(token.tokens))
            # process group and look if it starts with a nl
            if token.tokens and token.tokens[0].is_whitespace():
                before, rest = token.tokens[0].value.split('\n', 1)
                token.tokens[0].value = '\n%s' % rest
                buff = []
            while buff:
                yield buff.pop(0)
            yield token
        else:
            while buff:
                yield buff.pop(0)
            yield token


# --------------------------
# token process

class _CaseFilter(TokenFilter):

    ttype = None

    def __init__(self, case=None):
        if case is None:
            case = 'upper'
        assert case in ['lower', 'upper', 'capitalize']
        self.convert = getattr(unicode, case)

    def process(self, stack, stream):
        for ttype, value in stream:
            if ttype in self.ttype:
                value = self.convert(value)
            yield ttype, value


class KeywordCaseFilter(_CaseFilter):
    ttype = T.Keyword


class IdentifierCaseFilter(_CaseFilter):
    ttype = (T.Name, T.String.Symbol)


# ----------------------
# statement process

class StripCommentsFilter(Filter):

    def _process(self, tlist):
        idx = 0
        clss = set([x.__class__ for x in tlist.tokens])
        while grouping.Comment in clss:
            token = tlist.token_next_by_instance(0, grouping.Comment)
            tidx = tlist.token_index(token)
            prev = tlist.token_prev(tidx, False)
            next_ = tlist.token_next(tidx, False)
            # Replace by whitespace if prev and next exist and if they're not
            # whitespaces. This doesn't apply if prev or next is a paranthesis.
            if (prev is not None and next_ is not None
                and not prev.is_whitespace() and not next_.is_whitespace()
                and not (prev.match(T.Punctuation, '(')
                         or next_.match(T.Punctuation, ')'))):
                tlist.tokens[tidx] = grouping.Token(T.Whitespace, ' ')
            else:
                tlist.tokens.pop(tidx)
            clss = set([x.__class__ for x in tlist.tokens])

    def process(self, stack, stmt):
        [self.process(stack, sgroup) for sgroup in stmt.get_sublists()]
        self._process(stmt)


class StripWhitespaceFilter(Filter):

    def _stripws(self, tlist):
        func_name = '_stripws_%s' % tlist.__class__.__name__.lower()
        func = getattr(self, func_name, self._stripws_default)
        func(tlist)

    def _stripws_default(self, tlist):
        last_was_ws = False
        for token in tlist.tokens:
            if token.is_whitespace():
                if last_was_ws:
                    token.value = ''
                else:
                    token.value = ' '
            last_was_ws = token.is_whitespace()

    def _stripws_parenthesis(self, tlist):
        if tlist.tokens[1].is_whitespace():
            tlist.tokens.pop(1)
        if tlist.tokens[-2].is_whitespace():
            tlist.tokens.pop(-2)
        self._stripws_default(tlist)

    def process(self, stack, stmt):
        [self.process(stack, sgroup) for sgroup in stmt.get_sublists()]
        self._stripws(stmt)
        if stmt.tokens[-1].is_whitespace():
            stmt.tokens.pop(-1)


class ReindentFilter(Filter):

    def __init__(self, width=2, char=' ', line_width=None):
        self.width = width
        self.char = char
        self.indent = 0
        self.offset = 0
        self.line_width = line_width
        self._curr_stmt = None
        self._last_stmt = None

    def _get_offset(self, token):
        all_ = list(self._curr_stmt.flatten())
        idx = all_.index(token)
        raw = ''.join(unicode(x) for x in all_[:idx+1])
        line = raw.splitlines()[-1]
        # Now take current offset into account and return relative offset.
        full_offset = len(line)-(len(self.char*(self.width*self.indent)))
        return full_offset - self.offset

    def nl(self):
        # TODO: newline character should be configurable
        ws = '\n'+(self.char*((self.indent*self.width)+self.offset))
        return grouping.Token(T.Whitespace, ws)

    def _split_kwds(self, tlist):
        split_words = ('FROM', 'JOIN$', 'AND', 'OR',
                       'GROUP', 'ORDER', 'UNION', 'VALUES',
                       'SET')
        idx = 0
        token = tlist.token_next_match(idx, T.Keyword, split_words,
                                       regex=True)
        while token:
            prev = tlist.token_prev(tlist.token_index(token), False)
            offset = 1
            if prev and prev.is_whitespace():
                tlist.tokens.pop(tlist.token_index(prev))
                offset += 1
            if (prev
                and isinstance(prev, sql.Comment)
                and (str(prev).endswith('\n')
                     or str(prev).endswith('\r'))):
                nl = tlist.token_next(token)
            else:
                nl = self.nl()
                tlist.insert_before(token, nl)
            token = tlist.token_next_match(tlist.token_index(nl)+offset,
                                           T.Keyword, split_words, regex=True)

    def _split_statements(self, tlist):
        idx = 0
        token = tlist.token_next_by_type(idx, (T.Keyword.DDL, T.Keyword.DML))
        while token:
            prev = tlist.token_prev(tlist.token_index(token), False)
            if prev and prev.is_whitespace():
                tlist.tokens.pop(tlist.token_index(prev))
            # only break if it's not the first token
            if prev:
                nl = self.nl()
                tlist.insert_before(token, nl)
            token = tlist.token_next_by_type(tlist.token_index(token)+1,
                                             (T.Keyword.DDL, T.Keyword.DML))

    def _process(self, tlist):
        func_name = '_process_%s' % tlist.__class__.__name__.lower()
        func = getattr(self, func_name, self._process_default)
        func(tlist)

    def _process_where(self, tlist):
        token = tlist.token_next_match(0, T.Keyword, 'WHERE')
        tlist.insert_before(token, self.nl())
        self.indent += 1
        self._process_default(tlist)
        self.indent -= 1

    def _process_parenthesis(self, tlist):
        first = tlist.token_next(0)
        indented = False
        if first and first.ttype in (T.Keyword.DML, T.Keyword.DDL):
            self.indent += 1
            tlist.tokens.insert(0, self.nl())
            indented = True
        num_offset = self._get_offset(tlist.token_next_match(0,
                                                        T.Punctuation, '('))
        self.offset += num_offset
        self._process_default(tlist, stmts=not indented)
        if indented:
            self.indent -= 1
        self.offset -= num_offset

    def _process_identifierlist(self, tlist):
        identifiers = tlist.get_identifiers()
        if len(identifiers) > 1:
            first = list(identifiers[0].flatten())[0]
            num_offset = self._get_offset(first)-len(first.value)
            self.offset += num_offset
            for token in identifiers[1:]:
                tlist.insert_before(token, self.nl())
            self.offset -= num_offset
        self._process_default(tlist)

    def _process_case(self, tlist):
        cases = tlist.get_cases()
        is_first = True
        num_offset = None
        case = tlist.tokens[0]
        outer_offset = self._get_offset(case)-len(case.value)
        self.offset += outer_offset
        for cond, value in tlist.get_cases():
            if is_first:
                is_first = False
                num_offset = self._get_offset(cond[0])-len(cond[0].value)
                self.offset += num_offset
                continue
            if cond is None:
                token = value[0]
            else:
                token = cond[0]
            tlist.insert_before(token, self.nl())
        # Line breaks on group level are done. Now let's add an offset of
        # 5 (=length of "when", "then", "else") and process subgroups.
        self.offset += 5
        self._process_default(tlist)
        self.offset -= 5
        if num_offset is not None:
            self.offset -= num_offset
        end = tlist.token_next_match(0, T.Keyword, 'END')
        tlist.insert_before(end, self.nl())
        self.offset -= outer_offset

    def _process_default(self, tlist, stmts=True, kwds=True):
        if stmts:
            self._split_statements(tlist)
        if kwds:
            self._split_kwds(tlist)
        [self._process(sgroup) for sgroup in tlist.get_sublists()]

    def process(self, stack, stmt):
        if isinstance(stmt, grouping.Statement):
            self._curr_stmt = stmt
        self._process(stmt)
        if isinstance(stmt, grouping.Statement):
            if self._last_stmt is not None:
                if self._last_stmt.to_unicode().endswith('\n'):
                    nl = '\n'
                else:
                    nl = '\n\n'
                stmt.tokens.insert(0,
                    grouping.Token(T.Whitespace, nl))
            if self._last_stmt != stmt:
                self._last_stmt = stmt


# FIXME: Doesn't work ;)
class RightMarginFilter(Filter):

    keep_together = (
#        grouping.TypeCast, grouping.Identifier, grouping.Alias,
    )

    def __init__(self, width=79):
        self.width = width
        self.line = ''

    def _process(self, stack, group, stream):
        for token in stream:
            if token.is_whitespace() and '\n' in token.value:
                if token.value.endswith('\n'):
                    self.line = ''
                else:
                    self.line = token.value.splitlines()[-1]
            elif (token.is_group()
                  and not token.__class__ in self.keep_together):
                token.tokens = self._process(stack, token, token.tokens)
            else:
                val = token.to_unicode()
                if len(self.line) + len(val) > self.width:
                    match = re.search('^ +', self.line)
                    if match is not None:
                        indent = match.group()
                    else:
                        indent = ''
                    yield grouping.Token(T.Whitespace, '\n%s' % indent)
                    self.line = indent
                self.line += val
            yield token

    def process(self, stack, group):
        return
        group.tokens = self._process(stack, group, group.tokens)


# ---------------------------
# postprocess

class SerializerUnicode(Filter):

    def process(self, stack, stmt):
        raw = stmt.to_unicode()
        add_nl = raw.endswith('\n')
        res = '\n'.join(line.rstrip() for line in raw.splitlines())
        if add_nl:
            res += '\n'
        return res


class OutputPythonFilter(Filter):

    def __init__(self, varname='sql'):
        self.varname = varname
        self.cnt = 0

    def _process(self, stream, varname, count, has_nl):
        if count > 1:
            yield grouping.Token(T.Whitespace, '\n')
        yield grouping.Token(T.Name, varname)
        yield grouping.Token(T.Whitespace, ' ')
        yield grouping.Token(T.Operator, '=')
        yield grouping.Token(T.Whitespace, ' ')
        if has_nl:
            yield grouping.Token(T.Operator, '(')
        yield grouping.Token(T.Text, "'")
        cnt = 0
        for token in stream:
            cnt += 1
            if token.is_whitespace() and '\n' in token.value:
                if cnt == 1:
                    continue
                after_lb = token.value.split('\n', 1)[1]
                yield grouping.Token(T.Text, " '")
                yield grouping.Token(T.Whitespace, '\n')
                for i in range(len(varname)+4):
                    yield grouping.Token(T.Whitespace, ' ')
                yield grouping.Token(T.Text, "'")
                if after_lb:  # it's the indendation
                    yield grouping.Token(T.Whitespace, after_lb)
                continue
            elif token.value and "'" in token.value:
                token.value = token.value.replace("'", "\\'")
            yield grouping.Token(T.Text, token.value or '')
        yield grouping.Token(T.Text, "'")
        if has_nl:
            yield grouping.Token(T.Operator, ')')

    def process(self, stack, stmt):
        self.cnt += 1
        if self.cnt > 1:
            varname = '%s%d' % (self.varname, self.cnt)
        else:
            varname = self.varname
        has_nl = len(stmt.to_unicode().strip().splitlines()) > 1
        stmt.tokens = self._process(stmt.tokens, varname, self.cnt, has_nl)
        return stmt


class OutputPHPFilter(Filter):

    def __init__(self, varname='sql'):
        self.varname = '$%s' % varname
        self.count = 0

    def _process(self, stream, varname):
        if self.count > 1:
            yield grouping.Token(T.Whitespace, '\n')
        yield grouping.Token(T.Name, varname)
        yield grouping.Token(T.Whitespace, ' ')
        yield grouping.Token(T.Operator, '=')
        yield grouping.Token(T.Whitespace, ' ')
        yield grouping.Token(T.Text, '"')
        cnt = 0
        for token in stream:
            if token.is_whitespace() and '\n' in token.value:
#                cnt += 1
#                if cnt == 1:
#                    continue
                after_lb = token.value.split('\n', 1)[1]
                yield grouping.Token(T.Text, ' "')
                yield grouping.Token(T.Operator, ';')
                yield grouping.Token(T.Whitespace, '\n')
                yield grouping.Token(T.Name, varname)
                yield grouping.Token(T.Whitespace, ' ')
                yield grouping.Token(T.Punctuation, '.')
                yield grouping.Token(T.Operator, '=')
                yield grouping.Token(T.Whitespace, ' ')
                yield grouping.Token(T.Text, '"')
                if after_lb:
                    yield grouping.Token(T.Text, after_lb)
                continue
            elif '"' in token.value:
                token.value = token.value.replace('"', '\\"')
            yield grouping.Token(T.Text, token.value)
        yield grouping.Token(T.Text, '"')
        yield grouping.Token(T.Punctuation, ';')

    def process(self, stack, stmt):
        self.count += 1
        if self.count > 1:
            varname = '%s%d' % (self.varname, self.count)
        else:
            varname = self.varname
        stmt.tokens = tuple(self._process(stmt.tokens, varname))
        return stmt

