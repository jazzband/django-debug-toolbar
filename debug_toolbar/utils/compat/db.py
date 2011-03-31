try:
    from django.db import connections
except ImportError:
    # Compat with < Django 1.2
    from django.db import connection
    connections = {'default': connection}