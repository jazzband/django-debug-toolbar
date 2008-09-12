import simplejson
from django.db import connection
from django.shortcuts import render_to_response
from debug_toolbar.panels.sql import reformat_sql

def explain(request):
    """
    Returns the output of the SQL EXPLAIN on the given query.
    
    Expected GET variables:
        sql: urlencoded sql with position arguments
        params: JSON encoded parameter values
        time: time for SQL to execute passed in from toolbar just for redisplay
    """
    sql = request.GET.get('sql', '')
    if sql.lower().startswith('select'):
        params = simplejson.loads(request.GET.get('params', ''))
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
        