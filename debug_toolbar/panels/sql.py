from datetime import datetime
import os
import sys
import SocketServer
import traceback

import django
from django.conf import settings
from django.db import connection
from django.db.backends import util
from django.views.debug import linebreak_iter
from django.template import Node
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.hashcompat import sha_constructor
from django.utils.translation import ugettext_lazy as _

from debug_toolbar.panels import DebugPanel
from debug_toolbar.utils import sqlparse

# Figure out some paths
django_path = os.path.realpath(os.path.dirname(django.__file__))
socketserver_path = os.path.realpath(os.path.dirname(SocketServer.__file__))

# TODO:This should be set in the toolbar loader as a default and panels should
# get a copy of the toolbar object with access to its config dictionary
SQL_WARNING_THRESHOLD = getattr(settings, 'DEBUG_TOOLBAR_CONFIG', {}) \
                            .get('SQL_WARNING_THRESHOLD', 500)

def tidy_stacktrace(strace):
    """
    Clean up stacktrace and remove all entries that:
    1. Are part of Django (except contrib apps)
    2. Are part of SocketServer (used by Django's dev server)
    3. Are the last entry (which is part of our stacktracing code)
    """
    trace = []
    for s in strace[:-1]:
        s_path = os.path.realpath(s[0])
        if getattr(settings, 'DEBUG_TOOLBAR_CONFIG', {}).get('HIDE_DJANGO_SQL', True) \
            and django_path in s_path and not 'django/contrib' in s_path:
            continue
        if socketserver_path in s_path:
            continue
        trace.append((s[0], s[1], s[2], s[3]))
    return trace

def get_template_info(source, context_lines=3):
    line = 0
    upto = 0
    source_lines = []
    before = during = after = ""

    origin, (start, end) = source
    template_source = origin.reload()

    for num, next in enumerate(linebreak_iter(template_source)):
        if start >= upto and end <= next:
            line = num
            before = template_source[upto:start]
            during = template_source[start:end]
            after = template_source[end:next]
        source_lines.append((num, template_source[upto:next]))
        upto = next

    top = max(1, line - context_lines)
    bottom = min(len(source_lines), line + 1 + context_lines)

    context = []
    for num, content in source_lines[top:bottom]:
        context.append({
            'num': num,
            'content': content,
            'highlight': (num == line),
        })

    return {
        'name': origin.name,
        'context': context,
    }

class DatabaseStatTracker(util.CursorDebugWrapper):
    """
    Replacement for CursorDebugWrapper which stores additional information
    in `connection.queries`.
    """
    def execute(self, sql, params=()):
        start = datetime.now()
        try:
            return self.cursor.execute(sql, params)
        finally:
            stop = datetime.now()
            duration = ms_from_timedelta(stop - start)
            stacktrace = tidy_stacktrace(traceback.extract_stack())
            _params = ''
            try:
                _params = simplejson.dumps([force_unicode(x, strings_only=True) for x in params])
            except TypeError:
                pass # object not JSON serializable

            template_info = None
            cur_frame = sys._getframe().f_back
            try:
                while cur_frame is not None:
                    if cur_frame.f_code.co_name == 'render':
                        node = cur_frame.f_locals['self']
                        if isinstance(node, Node):
                            template_info = get_template_info(node.source)
                            break
                    cur_frame = cur_frame.f_back
            except:
                pass
            del cur_frame

            # We keep `sql` to maintain backwards compatibility
            self.db.queries.append({
                'sql': self.db.ops.last_executed_query(self.cursor, sql, params),
                'duration': duration,
                'raw_sql': sql,
                'params': _params,
                'hash': sha_constructor(settings.SECRET_KEY + sql + _params).hexdigest(),
                'stacktrace': stacktrace,
                'start_time': start,
                'stop_time': stop,
                'is_slow': (duration > SQL_WARNING_THRESHOLD),
                'is_select': sql.lower().strip().startswith('select'),
                'template_info': template_info,
            })
util.CursorDebugWrapper = DatabaseStatTracker

class SQLDebugPanel(DebugPanel):
    """
    Panel that displays information about the SQL queries run while processing
    the request.
    """
    name = 'SQL'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self._offset = len(connection.queries)
        self._sql_time = 0
        self._queries = []

    def nav_title(self):
        return _('SQL')

    def nav_subtitle(self):
        self._queries = connection.queries[self._offset:]
        self._sql_time = sum([q['duration'] for q in self._queries])
        num_queries = len(self._queries)
        # TODO l10n: use ngettext
        return "%d %s in %.2fms" % (
            num_queries,
            (num_queries == 1) and 'query' or 'queries',
            self._sql_time
        )

    def title(self):
        return _('SQL Queries')

    def url(self):
        return ''

    def content(self):
        width_ratio_tally = 0
        for query in self._queries:
            query['sql'] = reformat_sql(query['sql'])
            try:
                query['width_ratio'] = (query['duration'] / self._sql_time) * 100
            except ZeroDivisionError:
                query['width_ratio'] = 0
            query['start_offset'] = width_ratio_tally
            width_ratio_tally += query['width_ratio']

        context = self.context.copy()
        context.update({
            'queries': self._queries,
            'sql_time': self._sql_time,
            'is_mysql': settings.DATABASE_ENGINE == 'mysql',
        })

        return render_to_string('debug_toolbar/panels/sql.html', context)

def ms_from_timedelta(td):
    """
    Given a timedelta object, returns a float representing milliseconds
    """
    return (td.seconds * 1000) + (td.microseconds / 1000.0)

class BoldKeywordFilter(sqlparse.filters.Filter):
    """sqlparse filter to bold SQL keywords"""
    def process(self, stack, stream):
        """Process the token stream"""
        for token_type, value in stream:
            is_keyword = token_type in sqlparse.tokens.Keyword
            if is_keyword:
                yield sqlparse.tokens.Text, '<strong>'
            yield token_type, django.utils.html.escape(value)
            if is_keyword:
                yield sqlparse.tokens.Text, '</strong>'

def reformat_sql(sql):
    stack = sqlparse.engine.FilterStack()
    stack.preprocess.append(BoldKeywordFilter()) # add our custom filter
    stack.postprocess.append(sqlparse.filters.SerializerUnicode()) # tokens -> strings
    return ''.join(stack.run(sql))
