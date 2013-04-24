import re
from debug_toolbar.utils import sqlparse
from debug_toolbar.utils.sqlparse.filters import BoldKeywordFilter


def reformat_sql(sql):
    stack = sqlparse.engine.FilterStack()
    stack.preprocess.append(BoldKeywordFilter())  # add our custom filter
    stack.postprocess.append(sqlparse.filters.SerializerUnicode())  # tokens -> strings
    return swap_fields(''.join(stack.run(sql)))


def swap_fields(sql):
    return re.sub('SELECT</strong> (.*?) <strong>FROM', 'SELECT</strong> <a class="djDebugUncollapsed djDebugToggle" href="#">&bull;&bull;&bull;</a> ' +
        '<a class="djDebugCollapsed djDebugToggle" href="#">\g<1></a> <strong>FROM', sql)
