# -*- coding: utf-8 -*-

import itertools
import re
import types

from debug_toolbar.utils.sqlparse import tokens as T
from debug_toolbar.utils.sqlparse.sql import *



def _group_left_right(tlist, ttype, value, cls,
                      check_right=lambda t: True,
                      include_semicolon=False):
    [_group_left_right(sgroup, ttype, value, cls, check_right,
                       include_semicolon) for sgroup in tlist.get_sublists()
     if not isinstance(sgroup, cls)]
    idx = 0
    token = tlist.token_next_match(idx, ttype, value)
    while token:
        right = tlist.token_next(tlist.token_index(token))
        left = tlist.token_prev(tlist.token_index(token))
        if (right is None or not check_right(right)
            or left is None):
            token = tlist.token_next_match(tlist.token_index(token)+1,
                                           ttype, value)
        else:
            if include_semicolon:
                right = tlist.token_next_match(tlist.token_index(right),
                                               T.Punctuation, ';')
            tokens = tlist.tokens_between(left, right)[1:]
            if not isinstance(left, cls):
                new = cls([left])
                new_idx = tlist.token_index(left)
                tlist.tokens.remove(left)
                tlist.tokens.insert(new_idx, new)
                left = new
            left.tokens.extend(tokens)
            for t in tokens:
                tlist.tokens.remove(t)
            token = tlist.token_next_match(tlist.token_index(left)+1,
                                           ttype, value)

def _group_matching(tlist, start_ttype, start_value, end_ttype, end_value,
                    cls, include_semicolon=False, recurse=False):
    def _find_matching(i, tl, stt, sva, ett, eva):
        depth = 1
        for t in tl.tokens[i:]:
            if t.match(stt, sva):
                depth += 1
            elif t.match(ett, eva):
                depth -= 1
                if depth == 1:
                    return t
        return None
    [_group_matching(sgroup, start_ttype, start_value, end_ttype, end_value,
                     cls, include_semicolon) for sgroup in tlist.get_sublists()
     if recurse]
    if isinstance(tlist, cls):
        idx = 1
    else:
        idx = 0
    token = tlist.token_next_match(idx, start_ttype, start_value)
    while token:
        tidx = tlist.token_index(token)
        end = _find_matching(tidx, tlist, start_ttype, start_value,
                             end_ttype, end_value)
        if end is None:
            idx = tidx+1
        else:
            if include_semicolon:
                next_ = tlist.token_next(tlist.token_index(end))
                if next_ and next_.match(T.Punctuation, ';'):
                    end = next_
            group = tlist.group_tokens(cls, tlist.tokens_between(token, end))
            _group_matching(group, start_ttype, start_value,
                            end_ttype, end_value, cls, include_semicolon)
            idx = tlist.token_index(group)+1
        token = tlist.token_next_match(idx, start_ttype, start_value)

def group_if(tlist):
    _group_matching(tlist, T.Keyword, 'IF', T.Keyword, 'END IF', If, True)

def group_for(tlist):
    _group_matching(tlist, T.Keyword, 'FOR', T.Keyword, 'END LOOP', For, True)

def group_as(tlist):
    _group_left_right(tlist, T.Keyword, 'AS', Identifier)

def group_assignment(tlist):
    _group_left_right(tlist, T.Assignment, ':=', Assignment,
                      include_semicolon=True)

def group_comparsion(tlist):
    _group_left_right(tlist, T.Operator, None, Comparsion)


def group_case(tlist):
    _group_matching(tlist, T.Keyword, 'CASE', T.Keyword, 'END', Case,
                    include_semicolon=True, recurse=True)


def group_identifier(tlist):
    def _consume_cycle(tl, i):
        x = itertools.cycle((lambda y: y.match(T.Punctuation, '.'),
                             lambda y: y.ttype in (T.String.Symbol,
                                                   T.Name,
                                                   T.Wildcard)))
        for t in tl.tokens[i:]:
            if x.next()(t):
                yield t
            else:
                raise StopIteration

    # bottom up approach: group subgroups first
    [group_identifier(sgroup) for sgroup in tlist.get_sublists()
     if not isinstance(sgroup, Identifier)]

    # real processing
    idx = 0
    token = tlist.token_next_by_type(idx, (T.String.Symbol, T.Name))
    while token:
        identifier_tokens = [token]+list(
            _consume_cycle(tlist,
                           tlist.token_index(token)+1))
        group = tlist.group_tokens(Identifier, identifier_tokens)
        idx = tlist.token_index(group)+1
        token = tlist.token_next_by_type(idx, (T.String.Symbol, T.Name))


def group_identifier_list(tlist):
    [group_identifier_list(sgroup) for sgroup in tlist.get_sublists()
     if not isinstance(sgroup, (Identifier, IdentifierList))]
    idx = 0
    # Allowed list items
    fend1_funcs = [lambda t: isinstance(t, Identifier),
                   lambda t: t.is_whitespace(),
                   lambda t: t.ttype == T.Wildcard,
                   lambda t: t.match(T.Keyword, 'null'),
                   lambda t: t.ttype == T.Number.Integer,
                   lambda t: t.ttype == T.String.Single,
                   lambda t: isinstance(t, Comparsion),
                   ]
    tcomma = tlist.token_next_match(idx, T.Punctuation, ',')
    start = None
    while tcomma is not None:
        before = tlist.token_prev(tcomma)
        after = tlist.token_next(tcomma)
        # Check if the tokens around tcomma belong to a list
        bpassed = apassed = False
        for func in fend1_funcs:
            if before is not None and func(before):
                bpassed = True
            if after is not None and func(after):
                apassed = True
        if not bpassed or not apassed:
            # Something's wrong here, skip ahead to next ","
            start = None
            tcomma = tlist.token_next_match(tlist.token_index(tcomma)+1,
                                            T.Punctuation, ',')
        else:
            if start is None:
                start = before
            next_ = tlist.token_next(after)
            if next_ is None or not next_.match(T.Punctuation, ','):
                # Reached the end of the list
                tokens = tlist.tokens_between(start, after)
                group = tlist.group_tokens(IdentifierList, tokens)
                start = None
                tcomma = tlist.token_next_match(tlist.token_index(group)+1,
                                                T.Punctuation, ',')
            else:
                tcomma = next_


def group_parenthesis(tlist):
    _group_matching(tlist, T.Punctuation, '(', T.Punctuation, ')', Parenthesis)

def group_comments(tlist):
    [group_comments(sgroup) for sgroup in tlist.get_sublists()
     if not isinstance(sgroup, Comment)]
    idx = 0
    token = tlist.token_next_by_type(idx, T.Comment)
    while token:
        tidx = tlist.token_index(token)
        end = tlist.token_not_matching(tidx+1,
                                       [lambda t: t.ttype in T.Comment,
                                        lambda t: t.is_whitespace()])
        if end is None:
            idx = tidx + 1
        else:
            eidx = tlist.token_index(end)
            grp_tokens = tlist.tokens_between(token,
                                              tlist.token_prev(eidx, False))
            group = tlist.group_tokens(Comment, grp_tokens)
            idx = tlist.token_index(group)
        token = tlist.token_next_by_type(idx, T.Comment)

def group_where(tlist):
    [group_where(sgroup) for sgroup in tlist.get_sublists()
     if not isinstance(sgroup, Where)]
    idx = 0
    token = tlist.token_next_match(idx, T.Keyword, 'WHERE')
    stopwords = ('ORDER', 'GROUP', 'LIMIT', 'UNION')
    while token:
        tidx = tlist.token_index(token)
        end = tlist.token_next_match(tidx+1, T.Keyword, stopwords)
        if end is None:
            end = tlist.tokens[-1]
        else:
            end = tlist.tokens[tlist.token_index(end)-1]
        group = tlist.group_tokens(Where, tlist.tokens_between(token, end))
        idx = tlist.token_index(group)
        token = tlist.token_next_match(idx, T.Keyword, 'WHERE')

def group_aliased(tlist):
    [group_aliased(sgroup) for sgroup in tlist.get_sublists()
     if not isinstance(sgroup, Identifier)]
    idx = 0
    token = tlist.token_next_by_instance(idx, Identifier)
    while token:
        next_ = tlist.token_next(tlist.token_index(token))
        if next_ is not None and isinstance(next_, Identifier):
            grp = tlist.tokens_between(token, next_)[1:]
            token.tokens.extend(grp)
            for t in grp:
                tlist.tokens.remove(t)
        idx = tlist.token_index(token)+1
        token = tlist.token_next_by_instance(idx, Identifier)


def group_typecasts(tlist):
    _group_left_right(tlist, T.Punctuation, '::', Identifier)


def group(tlist):
    for func in [group_parenthesis,
                 group_comments,
                 group_where,
                 group_case,
                 group_identifier,
                 group_typecasts,
                 group_as,
                 group_aliased,
                 group_assignment,
                 group_comparsion,
                 group_identifier_list,
                 group_if,
                 group_for,]:
        func(tlist)
