import sys

from datetime import datetime
from threading import local

from django.conf import settings
from django.template import Node
from django.utils.encoding import force_unicode, smart_str

from debug_toolbar.utils import ms_from_timedelta, tidy_stacktrace, \
                                get_template_info, get_stack
from debug_toolbar.utils.compat.db import connections

try:
    import json
except ImportError: # python < 2.6
    from django.utils import simplejson as json

try:
    from hashlib import sha1
except ImportError: # python < 2.5
    from django.utils.hashcompat import sha_constructor as sha1

# TODO:This should be set in the toolbar loader as a default and panels should
# get a copy of the toolbar object with access to its config dictionary
SQL_WARNING_THRESHOLD = getattr(settings, 'DEBUG_TOOLBAR_CONFIG', {}) \
                            .get('SQL_WARNING_THRESHOLD', 500)


class SQLQueryTriggered(Exception):
    """Thrown when template panel triggers a query"""
    pass


class ThreadLocalState(local):
    def __init__(self):
        self.enabled = True

    @property
    def Wrapper(self):
        if self.enabled:
            return NormalCursorWrapper
        return ExceptionCursorWrapper

    def recording(self, v):
        self.enabled = v


state = ThreadLocalState()
recording = state.recording  # export function


def CursorWrapper(*args, **kwds):  # behave like a class
    return state.Wrapper(*args, **kwds)


class ExceptionCursorWrapper(object):
    """
    Wraps a cursor and raises an exception on any operation.
    Used in Templates panel.
    """
    def __init__(self, cursor, db, logger):
        pass

    def __getattr__(self, attr):
        raise SQLQueryTriggered()


class NormalCursorWrapper(object):
    """
    Wraps a cursor and logs queries.
    """

    def __init__(self, cursor, db, logger):
        self.cursor = cursor
        # Instance of a BaseDatabaseWrapper subclass
        self.db = db
        # logger must implement a ``record`` method
        self.logger = logger

    def _quote_expr(self, element):
        if isinstance(element, basestring):
            element = element.replace("'", "''")
            return "'%s'" % element
        else:
            return repr(element)

    def _quote_params(self, params):
        if isinstance(params, dict):
            return dict((key, self._quote_expr(value))
                            for key, value in params.iteritems())
        return map(self._quote_expr, params)

    def _decode(self, param):
        try:
            return force_unicode(param, strings_only=True)
        except UnicodeDecodeError:
            return '(encoded string)'

    def execute(self, sql, params=()):
        start = datetime.now()
        try:
            return self.cursor.execute(sql, params)
        finally:
            # FIXME: Sometimes connections which are not in the connections
            # dict are used (for example in test database destroying).
            # The code below (at least get_transaction_id(alias) needs to have
            # the connection in the connections dict. It would be good to
            # not have this requirement at all, but for now lets just skip
            # these connections.
            if self.db.alias not in connections:
                return
            stop = datetime.now()
            duration = ms_from_timedelta(stop - start)
            enable_stacktraces = getattr(settings,
                'DEBUG_TOOLBAR_CONFIG', {}).get('ENABLE_STACKTRACES', True)
            if enable_stacktraces:
                stacktrace = tidy_stacktrace(reversed(get_stack()))
            else:
                stacktrace = []
            _params = ''
            try:
                _params = json.dumps(map(self._decode, params))
            except Exception:
                pass  # object not JSON serializable

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

            alias = getattr(self.db, 'alias', 'default')
            conn = self.db.connection
            # HACK: avoid imports
            if conn:
                engine = conn.__class__.__module__.split('.', 1)[0]
            else:
                engine = 'unknown'

            params = {
                'engine': engine,
                'alias': alias,
                'sql': self.db.ops.last_executed_query(self.cursor, sql,
                                                self._quote_params(params)),
                'duration': duration,
                'raw_sql': sql,
                'params': _params,
                'hash': sha1(settings.SECRET_KEY \
                                        + smart_str(sql) \
                                        + _params).hexdigest(),
                'stacktrace': stacktrace,
                'start_time': start,
                'stop_time': stop,
                'is_slow': (duration > SQL_WARNING_THRESHOLD),
                'is_select': sql.lower().strip().startswith('select'),
                'template_info': template_info,
            }

            if engine == 'psycopg2':
                # If an erroneous query was ran on the connection, it might
                # be in a state where checking isolation_level raises an
                # exception.
                try:
                    iso_level = conn.isolation_level
                except conn.InternalError:
                    iso_level = 'unknown'
                params.update({
                    'trans_id': self.logger.get_transaction_id(alias),
                    'trans_status': conn.get_transaction_status(),
                    'iso_level': iso_level,
                    'encoding': conn.encoding,
                })

            # We keep `sql` to maintain backwards compatibility
            self.logger.record(**params)

    def executemany(self, sql, param_list):
        return self.cursor.executemany(sql, param_list)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)
