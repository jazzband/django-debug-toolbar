from __future__ import unicode_literals

import sys

import json
from threading import local
from time import time

from django.template import Node
from django.utils.encoding import force_text
from django.utils import six

from debug_toolbar.utils import tidy_stacktrace, get_template_info, get_stack
from debug_toolbar.utils.settings import CONFIG


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
        if isinstance(element, six.string_types):
            return "'%s'" % force_text(element).replace("'", "''")
        else:
            return repr(element)

    def _quote_params(self, params):
        if not params:
            return params
        if isinstance(params, dict):
            return dict((key, self._quote_expr(value))
                        for key, value in params.items())
        return list(map(self._quote_expr, params))

    def _decode(self, param):
        try:
            return force_text(param, strings_only=True)
        except UnicodeDecodeError:
            return '(encoded string)'

    def execute(self, sql, params=()):
        start_time = time()
        try:
            return self.cursor.execute(sql, params)
        finally:
            stop_time = time()
            duration = (stop_time - start_time) * 1000
            if CONFIG['ENABLE_STACKTRACES']:
                stacktrace = tidy_stacktrace(reversed(get_stack()))
            else:
                stacktrace = []
            _params = ''
            try:
                _params = json.dumps(list(map(self._decode, params)))
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
            except Exception:
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
                'sql': self.db.ops.last_executed_query(
                    self.cursor, sql, self._quote_params(params)),
                'duration': duration,
                'raw_sql': sql,
                'params': _params,
                'stacktrace': stacktrace,
                'start_time': start_time,
                'stop_time': stop_time,
                'is_slow': duration > CONFIG['SQL_WARNING_THRESHOLD'],
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
