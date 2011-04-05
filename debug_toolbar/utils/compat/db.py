from django.conf import settings
try:
    from django.db import connections
    dbconf = settings.DATABASES
except ImportError:
    # Compat with < Django 1.2
    from django.db import connection
    connections = {'default': connection}
    dbconf = {
        'default': {
            'ENGINE': settings.DATABASE_ENGINE,
        }
    }