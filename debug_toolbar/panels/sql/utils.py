import re

import sqlparse
from django.utils.html import escape
from sqlparse import tokens as T


class BoldKeywordFilter:
    """sqlparse filter to bold SQL keywords"""

    def process(self, stream):
        """Process the token stream"""
        for token_type, value in stream:
            is_keyword = token_type in T.Keyword
            if is_keyword:
                yield T.Text, "<strong>"
            yield token_type, escape(value)
            if is_keyword:
                yield T.Text, "</strong>"


def reformat_sql(sql, with_toggle=False):
    formatted = parse_sql(sql, aligned_indent=True)
    if not with_toggle:
        return formatted
    simple = simplify(parse_sql(sql, aligned_indent=False))
    uncollapsed = '<span class="djDebugUncollapsed">{}</span>'.format(simple)
    collapsed = '<span class="djDebugCollapsed">{}</span>'.format(formatted)
    return collapsed + uncollapsed


def parse_sql(sql, aligned_indent=False):
    stack = sqlparse.engine.FilterStack()
    stack.enable_grouping()
    if aligned_indent:
        stack.stmtprocess.append(
            sqlparse.filters.AlignedIndentFilter(char="&nbsp;", n="<br/>")
        )
    stack.preprocess.append(BoldKeywordFilter())  # add our custom filter
    stack.postprocess.append(sqlparse.filters.SerializerUnicode())  # tokens -> strings
    return "".join(stack.run(sql))


def simplify(sql):
    expr = r"SELECT</strong> (...........*?) <strong>FROM"
    sub = r"SELECT</strong> &#8226;&#8226;&#8226; <strong>FROM"
    return re.sub(expr, sub, sql)


def contrasting_color_generator():
    """
    Generate constrasting colors by varying most significant bit of RGB first,
    and then vary subsequent bits systematically.
    """

    def rgb_to_hex(rgb):
        return "#%02x%02x%02x" % tuple(rgb)

    triples = [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
        (1, 1, 0),
        (0, 1, 1),
        (1, 0, 1),
        (1, 1, 1),
    ]
    n = 1 << 7
    so_far = [[0, 0, 0]]
    while True:
        if n == 0:  # This happens after 2**24 colours; presumably, never
            yield "#000000"  # black
        copy_so_far = list(so_far)
        for triple in triples:
            for previous in copy_so_far:
                rgb = [n * triple[i] + previous[i] for i in range(3)]
                so_far.append(rgb)
                yield rgb_to_hex(rgb)
        n >>= 1
