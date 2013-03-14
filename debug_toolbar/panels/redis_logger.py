# -*- coding: utf-8 -*-
import types
import inspect
from redis import StrictRedis
from datetime import datetime

from django.template.loader import render_to_string
from debug_toolbar.panels import DebugPanel



def ms_from_timedelta(td):
    """
    Given a timedelta object, returns a float representing milliseconds
    """
    return (td.seconds * 1000) + (td.microseconds / 1000.0)

def replace_call(func):
    def inner(callback):
        def wrapped(*args,**kwargs):
            return callback(func,*args,**kwargs)
        actual = getattr(func,'__wrapped__',func)
        wrapped.__wrapped__ = actual
        wrapped.__doc__ = getattr(actual,'__doc__',None)
        wrapped.__name__ = actual.__name__
        _replace_function(func,wrapped)
        return wrapped
    return inner

def _replace_function(func,wrapped):

    if isinstance(func,types.FunctionType):
        pass
    elif getattr(func,'im_self',None):
        pass
    elif hasattr(func,'im_class'):
        setattr(func.im_class,func.__name__,wrapped)
    else:
        raise

def _get_func_info():
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe,2)
    return calframe

def wrap_logger(logger):
    logger = logger
    def execute_command(func,self,*args,**options):

        start = datetime.now()
        try:
            result = func(self,*args,**options)
            return result
        finally:
            stop = datetime.now()
            command = args[0]
            arg = args[1]
            duration = ms_from_timedelta(stop - start)

            #TODO find more better way to get the calling func info
            calframe = _get_func_info()

            params = {
                'func':calframe[4][3],
                'func_path':"{}:{}".format(calframe[4][1],calframe[4][2]),
                'command':command,
                'arg':arg,
                'result':result,
                'start_time':start,
                'stop_time':stop,
                'duration':duration,
                'is_slow':None,

            }
            #TODO more better way to loggging?
            logger.record(**params)
    return execute_command


class RedisDebugPanel(DebugPanel):
    name = 'Redis'
    has_content = True

    def __init__(self,*args,**kwargs):
        super(RedisDebugPanel, self).__init__(*args, **kwargs)
        self._keys = list()
        self._num_commands = 0
        self._total_time = 0
        self.wrap_execute_command()

    def wrap_execute_command(self):
        replace_call(StrictRedis.execute_command)(wrap_logger(self))

    def record(self,**kwargs):
        self._keys.append(kwargs)
        self._total_time += kwargs['duration']
        self._num_commands += 1

    def title(self):
        return 'REDIS LOGGER'

    def nav_title(self):
        return 'REDIS LOGGER'

    def nav_subtitle(self):
        return "{} commands in {}ms".format(self._num_commands,
                                                self._total_time)

    def url(self):
        return ''

    def content(self):
        context = self.context.copy()
        context.update({
            'keys':self._keys,
        })
        return render_to_string('debug_toolbar/panels/redis_logger.html', context)


