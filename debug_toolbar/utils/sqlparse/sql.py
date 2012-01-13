# -*- coding: utf-8 -*-

"""This module contains classes representing syntactical elements of SQL."""

import re

from debug_toolbar.utils.sqlparse import tokens as T


class Token(object):
    """Base class for all other classes in this module.

    It represents a single token and has two instance attributes:
    ``value`` is the unchange value of the token and ``ttype`` is
    the type of the token.
    """

    __slots__ = ('value', 'ttype', 'parent')

    def __init__(self, ttype, value):
        self.value = value
        self.ttype = ttype
        self.parent = None

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        short = self._get_repr_value()
        return '<%s \'%s\' at 0x%07x>' % (self._get_repr_name(),
                                          short, id(self))

    def __unicode__(self):
        return self.value or ''

    def to_unicode(self):
        """Returns a unicode representation of this object."""
        return unicode(self)

    def _get_repr_name(self):
        return str(self.ttype).split('.')[-1]

    def _get_repr_value(self):
        raw = unicode(self)
        if len(raw) > 7:
            short = raw[:6] + u'...'
        else:
            short = raw
        return re.sub('\s+', ' ', short)

    def flatten(self):
        """Resolve subgroups."""
        yield self

    def match(self, ttype, values, regex=False):
        """Checks whether the token matches the given arguments.

        *ttype* is a token type. If this token doesn't match the given token
        type.
        *values* is a list of possible values for this token. The values
        are OR'ed together so if only one of the values matches ``True``
        is returned. Except for keyword tokens the comparison is
        case-sensitive. For convenience it's ok to pass in a single string.
        If *regex* is ``True`` (default is ``False``) the given values are
        treated as regular expressions.
        """
        type_matched = self.ttype is ttype
        if not type_matched or values is None:
            return type_matched
        if isinstance(values, basestring):
            values = set([values])
        if regex:
            if self.ttype is T.Keyword:
                values = set([re.compile(v, re.IGNORECASE) for v in values])
            else:
                values = set([re.compile(v) for v in values])
            for pattern in values:
                if pattern.search(self.value):
                    return True
            return False
        else:
            if self.ttype in T.Keyword:
                values = set([v.upper() for v in values])
                return self.value.upper() in values
            else:
                return self.value in values

    def is_group(self):
        """Returns ``True`` if this object has children."""
        return False

    def is_whitespace(self):
        """Return ``True`` if this token is a whitespace token."""
        return self.ttype and self.ttype in T.Whitespace

    def within(self, group_cls):
        """Returns ``True`` if this token is within *group_cls*.

        Use this method for example to check if an identifier is within
        a function: ``t.within(sql.Function)``.
        """
        parent = self.parent
        while parent:
            if isinstance(parent, group_cls):
                return True
            parent = parent.parent
        return False

    def is_child_of(self, other):
        """Returns ``True`` if this token is a direct child of *other*."""
        return self.parent == other

    def has_ancestor(self, other):
        """Returns ``True`` if *other* is in this tokens ancestry."""
        parent = self.parent
        while parent:
            if parent == other:
                return True
            parent = parent.parent
        return False


class TokenList(Token):
    """A group of tokens.

    It has an additional instance attribute ``tokens`` which holds a
    list of child-tokens.
    """

    __slots__ = ('value', 'ttype', 'tokens')

    def __init__(self, tokens=None):
        if tokens is None:
            tokens = []
        self.tokens = tokens
        Token.__init__(self, None, None)

    def __unicode__(self):
        return ''.join(unicode(x) for x in self.flatten())

    def __str__(self):
        return unicode(self).encode('utf-8')

    def _get_repr_name(self):
        return self.__class__.__name__

    def _pprint_tree(self, max_depth=None, depth=0):
        """Pretty-print the object tree."""
        indent = ' ' * (depth * 2)
        for idx, token in enumerate(self.tokens):
            if token.is_group():
                pre = ' +-'
            else:
                pre = ' | '
            print '%s%s%d %s \'%s\'' % (indent, pre, idx,
                                        token._get_repr_name(),
                                        token._get_repr_value())
            if (token.is_group() and (max_depth is None or depth < max_depth)):
                token._pprint_tree(max_depth, depth + 1)

    def flatten(self):
        """Generator yielding ungrouped tokens.

        This method is recursively called for all child tokens.
        """
        for token in self.tokens:
            if isinstance(token, TokenList):
                for item in token.flatten():
                    yield item
            else:
                yield token

    def is_group(self):
        return True

    def get_sublists(self):
        return [x for x in self.tokens if isinstance(x, TokenList)]

    @property
    def _groupable_tokens(self):
        return self.tokens

    def token_first(self, ignore_whitespace=True):
        """Returns the first child token.

        If *ignore_whitespace* is ``True`` (the default), whitespace
        tokens are ignored.
        """
        for token in self.tokens:
            if ignore_whitespace and token.is_whitespace():
                continue
            return token
        return None

    def token_next_by_instance(self, idx, clss):
        """Returns the next token matching a class.

        *idx* is where to start searching in the list of child tokens.
        *clss* is a list of classes the token should be an instance of.

        If no matching token can be found ``None`` is returned.
        """
        if isinstance(clss, (list, tuple)):
            clss = (clss,)
        if isinstance(clss, tuple):
            clss = tuple(clss)
        for token in self.tokens[idx:]:
            if isinstance(token, clss):
                return token
        return None

    def token_next_by_type(self, idx, ttypes):
        """Returns next matching token by it's token type."""
        if not isinstance(ttypes, (list, tuple)):
            ttypes = [ttypes]
        for token in self.tokens[idx:]:
            if token.ttype in ttypes:
                return token
        return None

    def token_next_match(self, idx, ttype, value, regex=False):
        """Returns next token where it's ``match`` method returns ``True``."""
        if not isinstance(idx, int):
            idx = self.token_index(idx)
        for token in self.tokens[idx:]:
            if token.match(ttype, value, regex):
                return token
        return None

    def token_not_matching(self, idx, funcs):
        for token in self.tokens[idx:]:
            passed = False
            for func in funcs:
                if func(token):
                    passed = True
                    break
            if not passed:
                return token
        return None

    def token_matching(self, idx, funcs):
        for token in self.tokens[idx:]:
            for i, func in enumerate(funcs):
                if func(token):
                    return token
        return None

    def token_prev(self, idx, skip_ws=True):
        """Returns the previous token relative to *idx*.

        If *skip_ws* is ``True`` (the default) whitespace tokens are ignored.
        ``None`` is returned if there's no previous token.
        """
        if idx is None:
            return None
        if not isinstance(idx, int):
            idx = self.token_index(idx)
        while idx != 0:
            idx -= 1
            if self.tokens[idx].is_whitespace() and skip_ws:
                continue
            return self.tokens[idx]

    def token_next(self, idx, skip_ws=True):
        """Returns the next token relative to *idx*.

        If *skip_ws* is ``True`` (the default) whitespace tokens are ignored.
        ``None`` is returned if there's no next token.
        """
        if idx is None:
            return None
        if not isinstance(idx, int):
            idx = self.token_index(idx)
        while idx < len(self.tokens) - 1:
            idx += 1
            if self.tokens[idx].is_whitespace() and skip_ws:
                continue
            return self.tokens[idx]

    def token_index(self, token):
        """Return list index of token."""
        return self.tokens.index(token)

    def tokens_between(self, start, end, exclude_end=False):
        """Return all tokens between (and including) start and end.

        If *exclude_end* is ``True`` (default is ``False``) the end token
        is included too.
        """
        # FIXME(andi): rename exclude_end to inlcude_end
        if exclude_end:
            offset = 0
        else:
            offset = 1
        end_idx = self.token_index(end) + offset
        start_idx = self.token_index(start)
        return self.tokens[start_idx:end_idx]

    def group_tokens(self, grp_cls, tokens, ignore_ws=False):
        """Replace tokens by an instance of *grp_cls*."""
        idx = self.token_index(tokens[0])
        if ignore_ws:
            while tokens and tokens[-1].is_whitespace():
                tokens = tokens[:-1]
        for t in tokens:
            self.tokens.remove(t)
        grp = grp_cls(tokens)
        for token in tokens:
            token.parent = grp
        grp.parent = self
        self.tokens.insert(idx, grp)
        return grp

    def insert_before(self, where, token):
        """Inserts *token* before *where*."""
        self.tokens.insert(self.token_index(where), token)


class Statement(TokenList):
    """Represents a SQL statement."""

    __slots__ = ('value', 'ttype', 'tokens')

    def get_type(self):
        """Returns the type of a statement.

        The returned value is a string holding an upper-cased reprint of
        the first DML or DDL keyword. If the first token in this group
        isn't a DML or DDL keyword "UNKNOWN" is returned.
        """
        first_token = self.token_first()
        if first_token is None:
            # An "empty" statement that either has not tokens at all
            # or only whitespace tokens.
            return 'UNKNOWN'
        elif first_token.ttype in (T.Keyword.DML, T.Keyword.DDL):
            return first_token.value.upper()
        else:
            return 'UNKNOWN'


class Identifier(TokenList):
    """Represents an identifier.

    Identifiers may have aliases or typecasts.
    """

    __slots__ = ('value', 'ttype', 'tokens')

    def has_alias(self):
        """Returns ``True`` if an alias is present."""
        return self.get_alias() is not None

    def get_alias(self):
        """Returns the alias for this identifier or ``None``."""
        kw = self.token_next_match(0, T.Keyword, 'AS')
        if kw is not None:
            alias = self.token_next(self.token_index(kw))
            if alias is None:
                return None
        else:
            next_ = self.token_next(0)
            if next_ is None or not isinstance(next_, Identifier):
                return None
            alias = next_
        if isinstance(alias, Identifier):
            return alias.get_name()
        else:
            return alias.to_unicode()

    def get_name(self):
        """Returns the name of this identifier.

        This is either it's alias or it's real name. The returned valued can
        be considered as the name under which the object corresponding to
        this identifier is known within the current statement.
        """
        alias = self.get_alias()
        if alias is not None:
            return alias
        return self.get_real_name()

    def get_real_name(self):
        """Returns the real name (object name) of this identifier."""
        # a.b
        dot = self.token_next_match(0, T.Punctuation, '.')
        if dot is None:
            return self.token_next_by_type(0, T.Name).value
        else:
            next_ = self.token_next_by_type(self.token_index(dot),
                                            (T.Name, T.Wildcard))
            if next_ is None:  # invalid identifier, e.g. "a."
                return None
            return next_.value

    def get_parent_name(self):
        """Return name of the parent object if any.

        A parent object is identified by the first occuring dot.
        """
        dot = self.token_next_match(0, T.Punctuation, '.')
        if dot is None:
            return None
        prev_ = self.token_prev(self.token_index(dot))
        if prev_ is None:  # something must be verry wrong here..
            return None
        return prev_.value

    def is_wildcard(self):
        """Return ``True`` if this identifier contains a wildcard."""
        token = self.token_next_by_type(0, T.Wildcard)
        return token is not None

    def get_typecast(self):
        """Returns the typecast or ``None`` of this object as a string."""
        marker = self.token_next_match(0, T.Punctuation, '::')
        if marker is None:
            return None
        next_ = self.token_next(self.token_index(marker), False)
        if next_ is None:
            return None
        return next_.to_unicode()


class IdentifierList(TokenList):
    """A list of :class:`~sqlparse.sql.Identifier`\'s."""

    __slots__ = ('value', 'ttype', 'tokens')

    def get_identifiers(self):
        """Returns the identifiers.

        Whitespaces and punctuations are not included in this list.
        """
        return [x for x in self.tokens
                if not x.is_whitespace() and not x.match(T.Punctuation, ',')]


class Parenthesis(TokenList):
    """Tokens between parenthesis."""
    __slots__ = ('value', 'ttype', 'tokens')

    @property
    def _groupable_tokens(self):
        return self.tokens[1:-1]


class Assignment(TokenList):
    """An assignment like 'var := val;'"""
    __slots__ = ('value', 'ttype', 'tokens')


class If(TokenList):
    """An 'if' clause with possible 'else if' or 'else' parts."""
    __slots__ = ('value', 'ttype', 'tokens')


class For(TokenList):
    """A 'FOR' loop."""
    __slots__ = ('value', 'ttype', 'tokens')


class Comparison(TokenList):
    """A comparison used for example in WHERE clauses."""
    __slots__ = ('value', 'ttype', 'tokens')


class Comment(TokenList):
    """A comment."""
    __slots__ = ('value', 'ttype', 'tokens')


class Where(TokenList):
    """A WHERE clause."""
    __slots__ = ('value', 'ttype', 'tokens')


class Case(TokenList):
    """A CASE statement with one or more WHEN and possibly an ELSE part."""

    __slots__ = ('value', 'ttype', 'tokens')

    def get_cases(self):
        """Returns a list of 2-tuples (condition, value).

        If an ELSE exists condition is None.
        """
        ret = []
        in_value = False
        in_condition = True
        for token in self.tokens:
            if token.match(T.Keyword, 'CASE'):
                continue
            elif token.match(T.Keyword, 'WHEN'):
                ret.append(([], []))
                in_condition = True
                in_value = False
            elif token.match(T.Keyword, 'ELSE'):
                ret.append((None, []))
                in_condition = False
                in_value = True
            elif token.match(T.Keyword, 'THEN'):
                in_condition = False
                in_value = True
            elif token.match(T.Keyword, 'END'):
                in_condition = False
                in_value = False
            if (in_condition or in_value) and not ret:
                # First condition withou preceding WHEN
                ret.append(([], []))
            if in_condition:
                ret[-1][0].append(token)
            elif in_value:
                ret[-1][1].append(token)
        return ret


class Function(TokenList):
    """A function or procedure call."""

    __slots__ = ('value', 'ttype', 'tokens')

    def get_parameters(self):
        """Return a list of parameters."""
        parenthesis = self.tokens[-1]
        for t in parenthesis.tokens:
            if isinstance(t, IdentifierList):
                return t.get_identifiers()
        return []
