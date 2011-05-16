import inspect
import sys

from datetime import datetime

from django.conf import settings
from django.template import Node
from django.utils import simplejson
from django.utils.encoding import force_unicode
from django.utils.hashcompat import sha_constructor

from debug_toolbar.utils import ms_from_timedelta, tidy_stacktrace, get_template_info
from debug_toolbar.utils.compat.db import connections
# TODO:This should be set in the toolbar loader as a default and panels should
# get a copy of the toolbar object with access to its config dictionary
SQL_WARNING_THRESHOLD = getattr(settings, 'DEBUG_TOOLBAR_CONFIG', {}) \
                            .get('SQL_WARNING_THRESHOLD', 500)

class CursorWrapper(object):
    """
    Wraps a cursor and logs queries.
    """
    
    def __init__(self, cursor, db, logger):
        self.cursor = cursor
        # Instance of a BaseDatabaseWrapper subclass
        self.db = db
        # logger must implement a ``record`` method
        self.logger = logger

    def execute(self, sql, params=()):
        __traceback_hide__ = True
        start = datetime.now()
        try:
            return self.cursor.execute(sql, params)
        finally:
            stop = datetime.now()
            duration = ms_from_timedelta(stop - start)
            stacktrace = tidy_stacktrace(reversed(inspect.stack()))
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

            alias = getattr(self.db, 'alias', 'default')
            conn = connections[alias].connection
            # HACK: avoid imports
            if conn:
                engine = conn.__class__.__module__.split('.', 1)[0]
            else:
                engine = 'unknown'

            params = {
                'engine': engine,
                'alias': alias,
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
            }

            if engine == 'psycopg2':
                params.update({
                    'trans_id': self.logger.get_transaction_id(alias),
                    'trans_status': conn.get_transaction_status(),
                    'iso_level': conn.isolation_level,
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