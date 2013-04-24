try:
    from django.utils.functional import cached_property
except ImportError:  # Django < 1.4
    class cached_property(object):
        """
        Decorator that creates converts a method with a single
        self argument into a property cached on the instance.
        """
        def __init__(self, func):
            self.func = func

        def __get__(self, instance, type):
            res = instance.__dict__[self.func.__name__] = self.func(instance)
            return res
