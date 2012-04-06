# Copyright (C) 2008 Andi Albrecht, albrecht.andi@gmail.com
#
# This module is part of python-sqlparse and is released under
# the BSD License: http://www.opensource.org/licenses/bsd-license.php.

# The Token implementation is based on pygment's token system written
# by Georg Brandl.
# http://pygments.org/

"""Tokens"""


class _TokenType(tuple):
    parent = None

    def split(self):
        buf = []
        node = self
        while node is not None:
            buf.append(node)
            node = node.parent
        buf.reverse()
        return buf

    def __contains__(self, val):
        return val is not None and (self is val or val[:len(self)] == self)

    def __getattr__(self, val):
        if not val or not val[0].isupper():
            return tuple.__getattribute__(self, val)
        new = _TokenType(self + (val,))
        setattr(self, val, new)
        new.parent = self
        return new

    def __hash__(self):
        return hash(tuple(self))

    def __repr__(self):
        return 'Token' + (self and '.' or '') + '.'.join(self)


Token = _TokenType()

# Special token types
Text = Token.Text
Whitespace = Text.Whitespace
Newline = Whitespace.Newline
Error = Token.Error
# Text that doesn't belong to this lexer (e.g. HTML in PHP)
Other = Token.Other

# Common token types for source code
Keyword = Token.Keyword
Name = Token.Name
Literal = Token.Literal
String = Literal.String
Number = Literal.Number
Punctuation = Token.Punctuation
Operator = Token.Operator
Comparison = Operator.Comparison
Wildcard = Token.Wildcard
Comment = Token.Comment
Assignment = Token.Assignement

# Generic types for non-source code
Generic = Token.Generic

# String and some others are not direct childs of Token.
# alias them:
Token.Token = Token
Token.String = String
Token.Number = Number

# SQL specific tokens
DML = Keyword.DML
DDL = Keyword.DDL
Command = Keyword.Command

Group = Token.Group
Group.Parenthesis = Token.Group.Parenthesis
Group.Comment = Token.Group.Comment
Group.Where = Token.Group.Where
