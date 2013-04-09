import logging
import time
import types
from django.utils.importlib import import_module

from debug_toolbar.utils import not_on_py3


@not_on_py3
def post_dispatch(func):
    def wrapped(callback):
        register_hook(func, 'after', callback)
        return callback
    return wrapped


@not_on_py3
def pre_dispatch(func):
    def wrapped(callback):
        register_hook(func, 'before', callback)
        return callback
    return wrapped


@not_on_py3
def replace_call(func):
    def inner(callback):
        def wrapped(*args, **kwargs):
            return callback(func, *args, **kwargs)

        actual = getattr(func, '__wrapped__', func)
        wrapped.__wrapped__ = actual
        wrapped.__doc__ = getattr(actual, '__doc__', None)
        wrapped.__name__ = actual.__name__

        _replace_function(func, wrapped)
        return wrapped
    return inner


def monkey_patch_call(obj, attr):
    func = getattr(obj, attr)

    def inner(callback):
        def wrapped(*args, **kwargs):
            return callback(func, *args, **kwargs)
        actual = getattr(func, '__wrapped__', func)
        wrapped.__wrapped__ = actual
        wrapped.__doc__ = getattr(actual, '__doc__', None)
        wrapped.__name__ = actual.__name__
        if hasattr(actual, '__self__'):
            setattr(wrapped, '__self__', actual.__self__)
        setattr(obj, attr, wrapped)
        return wrapped
    return inner


def fire_hook(hook, sender, **kwargs):
    try:
        for callback in callbacks[hook].get(id(sender), []):
            callback(sender=sender, **kwargs)
    except Exception as e:
        # Log the exception, dont mess w/ the underlying function
        logging.exception(e)


@not_on_py3
def _replace_function(func, wrapped):
    if isinstance(func, types.FunctionType):
        if func.__module__ == '__builtin__':
            # oh shit
            __builtins__[func] = wrapped
        else:
            module = import_module(func.__module__)
            setattr(module, func.__name__, wrapped)
    elif getattr(func, 'im_self', None):
        setattr(func.im_self, func.__name__, classmethod(wrapped))
    elif hasattr(func, 'im_class'):
        # for unbound methods
        setattr(func.im_class, func.__name__, wrapped)
    else:
        raise NotImplementedError

callbacks = {
    'before': {},
    'after': {},
}


@not_on_py3
def register_hook(func, hook, callback):
    """
    def myhook(sender, args, kwargs):
        print func, "executed
        print "args:", args
        print "kwargs:", kwargs
    register_hook(BaseDatabaseWrapper.cursor, 'before', myhook)
    """

    assert hook in ('before', 'after')

    def wrapped(*args, **kwargs):
        start = time.time()
        fire_hook('before', sender=wrapped.__wrapped__, args=args, kwargs=kwargs,
                  start=start)
        result = wrapped.__wrapped__(*args, **kwargs)
        stop = time.time()
        fire_hook('after', sender=wrapped.__wrapped__, args=args, kwargs=kwargs,
                  result=result, start=start, stop=stop)
    actual = getattr(func, '__wrapped__', func)
    wrapped.__wrapped__ = actual
    wrapped.__doc__ = getattr(actual, '__doc__', None)
    wrapped.__name__ = actual.__name__

    id_ = id(actual)
    if id_ not in callbacks[hook]:
        callbacks[hook][id_] = []
    callbacks[hook][id_].append(callback)

    _replace_function(func, wrapped)
