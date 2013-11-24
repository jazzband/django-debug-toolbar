from __future__ import absolute_import, unicode_literals

import re

from django.utils.html import escape

import sqlparse
from sqlparse import tokens as T


class BoldKeywordFilter:
    """sqlparse filter to bold SQL keywords"""
    def process(self, stack, stream):
        """Process the token stream"""
        for token_type, value in stream:
            is_keyword = token_type in T.Keyword
            if is_keyword:
                yield T.Text, '<strong>'
            yield token_type, escape(value)
            if is_keyword:
                yield T.Text, '</strong>'


def reformat_sql(sql):
    stack = sqlparse.engine.FilterStack()
    stack.preprocess.append(BoldKeywordFilter())  # add our custom filter
    stack.postprocess.append(sqlparse.filters.SerializerUnicode())  # tokens -> strings
    return swap_fields(''.join(stack.run(sql)))


def swap_fields(sql):
    expr = r'SELECT</strong> (...........*?) <strong>FROM'
    subs = (r'SELECT</strong> '
            r'<a class="djDebugUncollapsed djDebugToggle" href="#">&#8226;&#8226;&#8226;</a> '
            r'<a class="djDebugCollapsed djDebugToggle" href="#">\1</a> '
            r'<strong>FROM')
    return re.sub(expr, subs, sql)
