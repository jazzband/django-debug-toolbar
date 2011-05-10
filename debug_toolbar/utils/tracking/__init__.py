import logging
import time
import types

def post_dispatch(func):
    def wrapped(callback):
        register_hook(func, 'after', callback)
        return callback
    return wrapped

def pre_dispatch(func):
    def wrapped(callback):
        register_hook(func, 'before', callback)
        return callback
    return wrapped

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

def fire_hook(hook, sender, **kwargs):
    try:
        for callback in callbacks[hook].get(id(sender), []):
            callback(sender=sender, **kwargs)
    except Exception, e:
        # Log the exception, dont mess w/ the underlying function
        logging.exception(e)

def _replace_function(func, wrapped):
    if isinstance(func, types.FunctionType):
        if func.__module__ == '__builtin__':
            # oh shit
            __builtins__[func] = wrapped
        else:
            module = __import__(func.__module__, {}, {}, [func.__module__], 0)
            setattr(module, func.__name__, wrapped)
    elif getattr(func, 'im_self', None):
        # TODO: classmethods
        raise NotImplementedError
    elif hasattr(func, 'im_class'):
        # for unbound methods
        setattr(func.im_class, func.__name__, wrapped)
    else:
        raise NotImplementedError

callbacks = {
    'before': {},
    'after': {},
}

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