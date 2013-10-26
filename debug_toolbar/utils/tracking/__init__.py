from __future__ import unicode_literals


def replace_method(klass, method_name):
    original = getattr(klass, method_name)

    def inner(callback):
        def wrapped(*args, **kwargs):
            return callback(original, *args, **kwargs)

        actual = getattr(original, '__wrapped__', original)
        wrapped.__wrapped__ = actual
        wrapped.__doc__ = getattr(actual, '__doc__', None)
        wrapped.__name__ = actual.__name__

        setattr(klass, method_name, wrapped)
        return wrapped

    return inner
