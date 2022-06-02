from functools import lru_cache
from html import escape

import sqlparse
from sqlparse import tokens as T

from debug_toolbar import settings as dt_settings


class ElideSelectListsFilter:
    """sqlparse filter to elide the select list in SELECT ... FROM clauses"""

    def process(self, stream):
        for token_type, value in stream:
            yield token_type, value
            if token_type in T.Keyword and value.upper() == "SELECT":
                yield from self.elide_until_from(stream)

    @staticmethod
    def elide_until_from(stream):
        select_list_characters = 0
        select_list_tokens = []
        for token_type, value in stream:
            if token_type in T.Keyword and value.upper() == "FROM":
                # Do not elide a select list of 12 characters or fewer to preserve
                #    SELECT COUNT(*) FROM ...
                # and
                #    SELECT (1) AS `a` FROM ...
                # queries.
                if select_list_characters <= 12:
                    yield from select_list_tokens
                else:
                    # U+2022: Unicode character 'BULLET'
                    yield T.Other, " \u2022\u2022\u2022 "
                yield token_type, value
                break
            if select_list_characters <= 12:
                select_list_characters += len(value)
                select_list_tokens.append((token_type, value))


class BoldKeywordFilter:
    """sqlparse filter to bold SQL keywords"""

    def process(self, stream):
        for token_type, value in stream:
            is_keyword = token_type in T.Keyword
            if is_keyword:
                yield T.Other, "<strong>"
            yield token_type, value
            if is_keyword:
                yield T.Other, "</strong>"


def escaped_value(token):
    # Don't escape T.Whitespace tokens because AlignedIndentFilter inserts its tokens as
    # T.Whitesapce, and in our case those tokens are actually HTML.
    if token.ttype in (T.Other, T.Whitespace):
        return token.value
    return escape(token.value, quote=False)


class EscapedStringSerializer:
    """sqlparse post-processor to convert a Statement into a string escaped for
    inclusion in HTML ."""

    @staticmethod
    def process(stmt):
        return "".join(escaped_value(token) for token in stmt.flatten())


def reformat_sql(sql, with_toggle=False):
    formatted = parse_sql(sql)
    if not with_toggle:
        return formatted
    simplified = parse_sql(sql, simplify=True)
    uncollapsed = f'<span class="djDebugUncollapsed">{simplified}</span>'
    collapsed = f'<span class="djDebugCollapsed djdt-hidden">{formatted}</span>'
    return collapsed + uncollapsed


def parse_sql(sql, *, simplify=False):
    return _parse_sql(
        sql,
        prettify=dt_settings.get_config()["PRETTIFY_SQL"],
        simplify=simplify,
    )


@lru_cache(maxsize=128)
def _parse_sql(sql, *, prettify, simplify):
    stack = get_filter_stack(prettify=prettify, simplify=simplify)
    return "".join(stack.run(sql))


@lru_cache(maxsize=None)
def get_filter_stack(*, prettify, simplify):
    stack = sqlparse.engine.FilterStack()
    if prettify:
        stack.enable_grouping()
    if simplify:
        stack.preprocess.append(ElideSelectListsFilter())
    else:
        stack.stmtprocess.append(
            sqlparse.filters.AlignedIndentFilter(char="&nbsp;", n="<br/>")
        )
    stack.preprocess.append(BoldKeywordFilter())
    stack.postprocess.append(EscapedStringSerializer())  # Statement -> str
    return stack


def contrasting_color_generator():
    """
    Generate contrasting colors by varying most significant bit of RGB first,
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
