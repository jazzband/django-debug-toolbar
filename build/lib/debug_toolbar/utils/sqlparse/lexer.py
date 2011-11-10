# -*- coding: utf-8 -*-

# Copyright (C) 2008 Andi Albrecht, albrecht.andi@gmail.com
#
# This module is part of python-sqlparse and is released under
# the BSD License: http://www.opensource.org/licenses/bsd-license.php.

"""SQL Lexer"""

# This code is based on the SqlLexer in pygments.
# http://pygments.org/
# It's separated from the rest of pygments to increase performance
# and to allow some customizations.

import re

from debug_toolbar.utils.sqlparse import tokens
from debug_toolbar.utils.sqlparse.keywords import KEYWORDS, KEYWORDS_COMMON


class include(str):
    pass


class combined(tuple):
    """Indicates a state combined from multiple states."""

    def __new__(cls, *args):
        return tuple.__new__(cls, args)

    def __init__(self, *args):
        # tuple.__init__ doesn't do anything
        pass


def is_keyword(value):
    test = value.upper()
    return KEYWORDS_COMMON.get(test, KEYWORDS.get(test, tokens.Name)), value


def apply_filters(stream, filters, lexer=None):
    """
    Use this method to apply an iterable of filters to
    a stream. If lexer is given it's forwarded to the
    filter, otherwise the filter receives `None`.
    """

    def _apply(filter_, stream):
        for token in filter_.filter(lexer, stream):
            yield token

    for filter_ in filters:
        stream = _apply(filter_, stream)
    return stream


class LexerMeta(type):
    """
    Metaclass for Lexer, creates the self._tokens attribute from
    self.tokens on the first instantiation.
    """

    def _process_state(cls, unprocessed, processed, state):
        assert type(state) is str, "wrong state name %r" % state
        assert state[0] != '#', "invalid state name %r" % state
        if state in processed:
            return processed[state]
        tokenlist = processed[state] = []
        rflags = cls.flags
        for tdef in unprocessed[state]:
            if isinstance(tdef, include):
                # it's a state reference
                assert tdef != state, "circular state reference %r" % state
                tokenlist.extend(cls._process_state(
                    unprocessed, processed, str(tdef)))
                continue

            assert type(tdef) is tuple, "wrong rule def %r" % tdef

            try:
                rex = re.compile(tdef[0], rflags).match
            except Exception, err:
                raise ValueError(("uncompilable regex %r in state"
                                  " %r of %r: %s"
                                  % (tdef[0], state, cls, err)))

            assert type(tdef[1]) is tokens._TokenType or callable(tdef[1]), \
                   ('token type must be simple type or callable, not %r'
                    % (tdef[1],))

            if len(tdef) == 2:
                new_state = None
            else:
                tdef2 = tdef[2]
                if isinstance(tdef2, str):
                    # an existing state
                    if tdef2 == '#pop':
                        new_state = -1
                    elif tdef2 in unprocessed:
                        new_state = (tdef2,)
                    elif tdef2 == '#push':
                        new_state = tdef2
                    elif tdef2[:5] == '#pop:':
                        new_state = -int(tdef2[5:])
                    else:
                        assert False, 'unknown new state %r' % tdef2
                elif isinstance(tdef2, combined):
                    # combine a new state from existing ones
                    new_state = '_tmp_%d' % cls._tmpname
                    cls._tmpname += 1
                    itokens = []
                    for istate in tdef2:
                        assert istate != state, \
                               'circular state ref %r' % istate
                        itokens.extend(cls._process_state(unprocessed,
                                                          processed, istate))
                    processed[new_state] = itokens
                    new_state = (new_state,)
                elif isinstance(tdef2, tuple):
                    # push more than one state
                    for state in tdef2:
                        assert (state in unprocessed or
                                state in ('#pop', '#push')), \
                               'unknown new state ' + state
                    new_state = tdef2
                else:
                    assert False, 'unknown new state def %r' % tdef2
            tokenlist.append((rex, tdef[1], new_state))
        return tokenlist

    def process_tokendef(cls):
        cls._all_tokens = {}
        cls._tmpname = 0
        processed = cls._all_tokens[cls.__name__] = {}
        #tokendefs = tokendefs or cls.tokens[name]
        for state in cls.tokens.keys():
            cls._process_state(cls.tokens, processed, state)
        return processed

    def __call__(cls, *args, **kwds):
        if not hasattr(cls, '_tokens'):
            cls._all_tokens = {}
            cls._tmpname = 0
            if hasattr(cls, 'token_variants') and cls.token_variants:
                # don't process yet
                pass
            else:
                cls._tokens = cls.process_tokendef()

        return type.__call__(cls, *args, **kwds)


class Lexer(object):

    __metaclass__ = LexerMeta

    encoding = 'utf-8'
    stripall = False
    stripnl = False
    tabsize = 0
    flags = re.IGNORECASE

    tokens = {
        'root': [
            (r'--.*?(\r\n|\r|\n)', tokens.Comment.Single),
            # $ matches *before* newline, therefore we have two patterns
            # to match Comment.Single
            (r'--.*?$', tokens.Comment.Single),
            (r'(\r|\n|\r\n)', tokens.Newline),
            (r'\s+', tokens.Whitespace),
            (r'/\*', tokens.Comment.Multiline, 'multiline-comments'),
            (r':=', tokens.Assignment),
            (r'::', tokens.Punctuation),
            (r'[*]', tokens.Wildcard),
            (r'CASE\b', tokens.Keyword),  # extended CASE(foo)
            (r"`(``|[^`])*`", tokens.Name),
            (r"´(´´|[^´])*´", tokens.Name),
            (r'\$([a-zA-Z_][a-zA-Z0-9_]*)?\$', tokens.Name.Builtin),
            (r'\?{1}', tokens.Name.Placeholder),
            (r'[$:?%][a-zA-Z0-9_]+[^$:?%]?', tokens.Name.Placeholder),
            (r'@[a-zA-Z_][a-zA-Z0-9_]+', tokens.Name),
            (r'[a-zA-Z_][a-zA-Z0-9_]*(?=[.(])', tokens.Name),  # see issue39
            (r'[<>=~!]+', tokens.Operator.Comparison),
            (r'[+/@#%^&|`?^-]+', tokens.Operator),
            (r'0x[0-9a-fA-F]+', tokens.Number.Hexadecimal),
            (r'[0-9]*\.[0-9]+', tokens.Number.Float),
            (r'[0-9]+', tokens.Number.Integer),
            # TODO: Backslash escapes?
            (r"(''|'.*?[^\\]')", tokens.String.Single),
            # not a real string literal in ANSI SQL:
            (r'(""|".*?[^\\]")', tokens.String.Symbol),
            (r'(\[.*[^\]]\])', tokens.Name),
            (r'(LEFT |RIGHT )?(INNER |OUTER )?JOIN\b', tokens.Keyword),
            (r'END( IF| LOOP)?\b', tokens.Keyword),
            (r'NOT NULL\b', tokens.Keyword),
            (r'CREATE( OR REPLACE)?\b', tokens.Keyword.DDL),
            (r'[a-zA-Z_][a-zA-Z0-9_]*', is_keyword),
            (r'[;:()\[\],\.]', tokens.Punctuation),
        ],
        'multiline-comments': [
            (r'/\*', tokens.Comment.Multiline, 'multiline-comments'),
            (r'\*/', tokens.Comment.Multiline, '#pop'),
            (r'[^/\*]+', tokens.Comment.Multiline),
            (r'[/*]', tokens.Comment.Multiline)
        ]}

    def __init__(self):
        self.filters = []

    def add_filter(self, filter_, **options):
        from debug_toolbar.utils.sqlparse.filters import Filter
        if not isinstance(filter_, Filter):
            filter_ = filter_(**options)
        self.filters.append(filter_)

    def get_tokens(self, text, unfiltered=False):
        """
        Return an iterable of (tokentype, value) pairs generated from
        `text`. If `unfiltered` is set to `True`, the filtering mechanism
        is bypassed even if filters are defined.

        Also preprocess the text, i.e. expand tabs and strip it if
        wanted and applies registered filters.
        """
        if not isinstance(text, unicode):
            if self.encoding == 'guess':
                try:
                    text = text.decode('utf-8')
                    if text.startswith(u'\ufeff'):
                        text = text[len(u'\ufeff'):]
                except UnicodeDecodeError:
                    text = text.decode('latin1')
            elif self.encoding == 'chardet':
                try:
                    import chardet
                except ImportError:
                    raise ImportError('To enable chardet encoding guessing, '
                                      'please install the chardet library '
                                      'from http://chardet.feedparser.org/')
                enc = chardet.detect(text)
                text = text.decode(enc['encoding'])
            else:
                text = text.decode(self.encoding)
        if self.stripall:
            text = text.strip()
        elif self.stripnl:
            text = text.strip('\n')
        if self.tabsize > 0:
            text = text.expandtabs(self.tabsize)
#        if not text.endswith('\n'):
#            text += '\n'

        def streamer():
            for i, t, v in self.get_tokens_unprocessed(text):
                yield t, v
        stream = streamer()
        if not unfiltered:
            stream = apply_filters(stream, self.filters, self)
        return stream

    def get_tokens_unprocessed(self, text, stack=('root',)):
        """
        Split ``text`` into (tokentype, text) pairs.

        ``stack`` is the inital stack (default: ``['root']``)
        """
        pos = 0
        tokendefs = self._tokens
        statestack = list(stack)
        statetokens = tokendefs[statestack[-1]]
        known_names = {}
        while 1:
            for rexmatch, action, new_state in statetokens:
                m = rexmatch(text, pos)
                if m:
                    # print rex.pattern
                    value = m.group()
                    if value in known_names:
                        yield pos, known_names[value], value
                    elif type(action) is tokens._TokenType:
                        yield pos, action, value
                    elif hasattr(action, '__call__'):
                        ttype, value = action(value)
                        known_names[value] = ttype
                        yield pos, ttype, value
                    else:
                        for item in action(self, m):
                            yield item
                    pos = m.end()
                    if new_state is not None:
                        # state transition
                        if isinstance(new_state, tuple):
                            for state in new_state:
                                if state == '#pop':
                                    statestack.pop()
                                elif state == '#push':
                                    statestack.append(statestack[-1])
                                else:
                                    statestack.append(state)
                        elif isinstance(new_state, int):
                            # pop
                            del statestack[new_state:]
                        elif new_state == '#push':
                            statestack.append(statestack[-1])
                        else:
                            assert False, "wrong state def: %r" % new_state
                        statetokens = tokendefs[statestack[-1]]
                    break
            else:
                try:
                    if text[pos] == '\n':
                        # at EOL, reset state to "root"
                        pos += 1
                        statestack = ['root']
                        statetokens = tokendefs['root']
                        yield pos, tokens.Text, u'\n'
                        continue
                    yield pos, tokens.Error, text[pos]
                    pos += 1
                except IndexError:
                    break


def tokenize(sql):
    """Tokenize sql.

    Tokenize *sql* using the :class:`Lexer` and return a 2-tuple stream
    of ``(token type, value)`` items.
    """
    lexer = Lexer()
    return lexer.get_tokens(sql)
