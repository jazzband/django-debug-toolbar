from datetime import datetime
import os
import re
import sys
import SocketServer
import traceback

import django
from django.conf import settings
try:
    from django.db import connections
except ImportError:
    # Compat with < Django 1.2
    from django.db import connection
    connections = {'default': connection}
from django.db.backends import util, BaseDatabaseWrapper
from django.views.debug import linebreak_iter
from django.template import Node
from django.template.defaultfilters import escape
from django.template.loader import render_to_string
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.hashcompat import sha_constructor
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ungettext_lazy as __

from debug_toolbar.middleware import DebugToolbarMiddleware
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

def inject_sql_tracker(cls):
    """
    Injects a replacement execute method which records queries within the SQLPanel.
    """
    if getattr(cls.execute, 'is_tracked', False):
        return
    def execute(self, sql, params=()):
        djdt = DebugToolbarMiddleware.get_current()
        if not djdt:
            return cls.execute.__wrapped__(self, sql, params)

        panel = djdt.get_panel(SQLDebugPanel)
        start = datetime.now()
        try:
            return cls.execute.__wrapped__(self, sql, params)
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
            panel.record(**{
                'alias': getattr(self, 'alias', 'default'),
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
    execute.is_tracked = True
    execute.__wrapped__ = cls.execute

    cls.execute = execute

class CursorWrapper(object):
    def __init__(self, cursor, db):
        self.cursor = cursor
        self.db = db # Instance of a BaseDatabaseWrapper subclass

    def execute(self, sql, params=None):
        return self.cursor.execute(sql, params)

    def executemany(self, sql, param_list):
        return self.cursor.executemany(sql, param_list)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)

if not hasattr(util, 'CursorWrapper'):
    # Inject our CursorWrapper class
    util.CursorWrapper = CursorWrapper

def cursor(self):
    from django.conf import settings
    cursor = self._cursor()
    if settings.DEBUG:
        return self.make_debug_cursor(cursor)
    return util.CursorWrapper(cursor, self)

BaseDatabaseWrapper.cursor = cursor

inject_sql_tracker(util.CursorWrapper)
inject_sql_tracker(util.CursorDebugWrapper)

class SQLDebugPanel(DebugPanel):
    """
    Panel that displays information about the SQL queries run while processing
    the request.
    """
    name = 'SQL'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self._offset = dict((k, len(connections[k].queries)) for k in connections)
        self._sql_time = 0
        self._num_queries = 0
        self._queries = []
        self._databases = {}
    
    def record(self, alias, **kwargs):
        self._queries.append((alias, kwargs))
        if alias not in self._databases:
            self._databases[alias] = {
                'time_spent': kwargs['duration'],
                'num_queries': 1,
            }
        else:
            self._databases[alias]['time_spent'] += kwargs['duration']
            self._databases[alias]['num_queries'] += 1
        self._sql_time += kwargs['duration']
        self._num_queries += 1

    def nav_title(self):
        return _('SQL')

    def nav_subtitle(self):
        # TODO l10n: use ngettext
        return "%d %s in %.2fms" % (
            self._num_queries,
            (self._num_queries == 1) and 'query' or 'queries',
            self._sql_time
        )

    def title(self):
        count = len(self._databases)
        
        return __('SQL Queries from %(count)d connection', 'SQL Queries from %(count)d connections', count) % dict(
            count=count,
        )

    def url(self):
        return ''

    def content(self):
        if self._queries:
            width_ratio_tally = 0
            colors = [
                (256, 0, 0), # red
                (0, 256, 0), # blue
                (0, 0, 256), # green
            ]
            factor = int(256.0/(len(self._databases)*2.5))
            for n, db in enumerate(self._databases.itervalues()):
                rgb = [0, 0, 0]
                color = n % 3
                rgb[color] = 256 - n/3*factor
                nn = color
                # XXX: pretty sure this is horrible after so many aliases
                while rgb[color] < factor:
                    print rgb[color], factor
                    nc = min(256 - rgb[color], 256)
                    rgb[color] += nc
                    nn += 1
                    if nn > 2:
                        nn = 0
                    rgb[nn] = nc
                db['rgb_color'] = rgb
        
            for alias, query in self._queries:
                query['alias'] = alias
                query['sql'] = reformat_sql(query['sql'])
                query['rgb_color'] = self._databases[alias]['rgb_color']
                try:
                    query['width_ratio'] = (query['duration'] / self._sql_time) * 100
                except ZeroDivisionError:
                    query['width_ratio'] = 0
                query['start_offset'] = width_ratio_tally
                query['end_offset'] = query['width_ratio'] + query['start_offset']
                width_ratio_tally += query['width_ratio']
            
                stacktrace = []
                for frame in query['stacktrace']:
                    params = map(escape, frame[0].rsplit('/', 1) + list(frame[1:]))
                    stacktrace.append('<span class="path">{0}/</span><span class="file">{1}</span> in <span class="func">{3}</span>(<span class="lineno">{2}</span>)\n  <span class="code">{4}</span>"'.format(*params))
                query['stacktrace'] = mark_safe('\n'.join(stacktrace))
        
        context = self.context.copy()
        context.update({
            'databases': sorted(self._databases.items(), key=lambda x: -x[1]['time_spent']),
            'queries': [q for a, q in self._queries],
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

def swap_fields(sql):
    return re.sub('SELECT</strong> (.*) <strong>FROM', 'SELECT</strong> <span class="djDebugCollapse">\g<1></span> <strong>FROM', sql)

def reformat_sql(sql):
    stack = sqlparse.engine.FilterStack()
    stack.preprocess.append(BoldKeywordFilter()) # add our custom filter
    stack.postprocess.append(sqlparse.filters.SerializerUnicode()) # tokens -> strings
    return swap_fields(''.join(stack.run(sql)))
