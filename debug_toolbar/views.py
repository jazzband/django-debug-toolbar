"""
Helper views for the debug toolbar. These are dynamically installed when the
debug toolbar is displayed, and typically can do Bad Things, so hooking up these
views in any other way is generally not advised.
"""

import os
import django.views.static
from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson
from django.utils.hashcompat import sha_constructor

def debug_media(request, path):
    root = getattr(settings, 'DEBUG_TOOLBAR_MEDIA_ROOT', None)
    if root is None:
        parent = os.path.abspath(os.path.dirname(__file__))
        root = os.path.join(parent, 'media')
    return django.views.static.serve(request, path, root)

def sql_explain(request):
    """
    Returns the output of the SQL EXPLAIN on the given query.

    Expected GET variables:
        sql: urlencoded sql with positional arguments
        params: JSON encoded parameter values
        time: time for SQL to execute passed in from toolbar just for redisplay
        hash: the hash of (secret + sql + params) for tamper checking
    """
    from debug_toolbar.panels.sql import reformat_sql
    sql = request.GET.get('sql', '')
    params = request.GET.get('params', '')
    hash = sha_constructor(settings.SECRET_KEY + sql + params).hexdigest()
    if hash != request.GET.get('hash', ''):
        return HttpResponse('<h3>Tamper alert</h3>') # SQL Tampering alert
    if sql.lower().startswith('select'):
        params = simplejson.loads(params)
        cursor = connection.cursor()
        cursor.execute("EXPLAIN %s" % (sql,), params)
        headers = [d[0] for d in cursor.description]
        result = cursor.fetchall()
        cursor.close()
        context = {
            'result': result,
            'sql': reformat_sql(cursor.db.ops.last_executed_query(cursor, sql, params)),
            'time': request.GET.get('time', 0.0),
            'headers': headers,
        }
        return render_to_response('debug_toolbar/panels/sql_explain.html', context)
