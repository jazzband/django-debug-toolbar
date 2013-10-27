"""
Helper views for the debug toolbar. These are dynamically installed when the
debug toolbar is displayed, and typically can do Bad Things, so hooking up these
views in any other way is generally not advised.
"""

from __future__ import unicode_literals

from django.http import HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from debug_toolbar.forms import SQLSelectForm


@csrf_exempt
def sql_select(request):
    """Returns the output of the SQL SELECT statement"""
    form = SQLSelectForm(request.POST or None)

    if form.is_valid():
        sql = form.cleaned_data['raw_sql']
        params = form.cleaned_data['params']
        cursor = form.cursor
        cursor.execute(sql, params)
        headers = [d[0] for d in cursor.description]
        result = cursor.fetchall()
        cursor.close()
        context = {
            'result': result,
            'sql': form.reformat_sql(),
            'duration': form.cleaned_data['duration'],
            'headers': headers,
            'alias': form.cleaned_data['alias'],
        }
        return render(request, 'debug_toolbar/panels/sql_select.html', context)
    return HttpResponseBadRequest('Form errors')


@csrf_exempt
def sql_explain(request):
    """Returns the output of the SQL EXPLAIN on the given query"""
    form = SQLSelectForm(request.POST or None)

    if form.is_valid():
        sql = form.cleaned_data['raw_sql']
        params = form.cleaned_data['params']
        cursor = form.cursor

        conn = form.connection
        engine = conn.__class__.__module__.split('.', 1)[0]

        if engine == "sqlite3":
            # SQLite's EXPLAIN dumps the low-level opcodes generated for a query;
            # EXPLAIN QUERY PLAN dumps a more human-readable summary
            # See http://www.sqlite.org/lang_explain.html for details
            cursor.execute("EXPLAIN QUERY PLAN %s" % (sql,), params)
        elif engine == "psycopg2":
            cursor.execute("EXPLAIN ANALYZE %s" % (sql,), params)
        else:
            cursor.execute("EXPLAIN %s" % (sql,), params)

        headers = [d[0] for d in cursor.description]
        result = cursor.fetchall()
        cursor.close()
        context = {
            'result': result,
            'sql': form.reformat_sql(),
            'duration': form.cleaned_data['duration'],
            'headers': headers,
            'alias': form.cleaned_data['alias'],
        }
        return render(request, 'debug_toolbar/panels/sql_explain.html', context)
    return HttpResponseBadRequest('Form errors')


@csrf_exempt
def sql_profile(request):
    """Returns the output of running the SQL and getting the profiling statistics"""
    form = SQLSelectForm(request.POST or None)

    if form.is_valid():
        sql = form.cleaned_data['raw_sql']
        params = form.cleaned_data['params']
        cursor = form.cursor
        result = None
        headers = None
        result_error = None
        try:
            cursor.execute("SET PROFILING=1")  # Enable profiling
            cursor.execute(sql, params)  # Execute SELECT
            cursor.execute("SET PROFILING=0")  # Disable profiling
            # The Query ID should always be 1 here but I'll subselect to get
            # the last one just in case...
            cursor.execute("""
  SELECT  *
    FROM  information_schema.profiling
   WHERE  query_id = (
          SELECT  query_id
            FROM  information_schema.profiling
        ORDER BY  query_id DESC
           LIMIT  1
        )
""")
            headers = [d[0] for d in cursor.description]
            result = cursor.fetchall()
        except Exception:
            result_error = "Profiling is either not available or not supported by your database."
        cursor.close()
        context = {
            'result': result,
            'result_error': result_error,
            'sql': form.reformat_sql(),
            'duration': form.cleaned_data['duration'],
            'headers': headers,
            'alias': form.cleaned_data['alias'],
        }
        return render(request, 'debug_toolbar/panels/sql_profile.html', context)
    return HttpResponseBadRequest('Form errors')


def template_source(request):
    """
    Return the source of a template, syntax-highlighted by Pygments if
    it's available.
    """
    from django.template import TemplateDoesNotExist
    from django.utils.safestring import mark_safe
    from django.conf import settings

    template_name = request.GET.get('template', None)
    if template_name is None:
        return HttpResponseBadRequest('"template" key is required')

    from django.template.loader import find_template_loader
    loaders = []
    for loader_name in settings.TEMPLATE_LOADERS:
        loader = find_template_loader(loader_name)
        if loader is not None:
            loaders.append(loader)
    for loader in loaders:
        try:
            source, display_name = loader.load_template_source(template_name)
            break
        except TemplateDoesNotExist:
            source = "Template Does Not Exist: %s" % (template_name,)

    try:
        from pygments import highlight
        from pygments.lexers import HtmlDjangoLexer
        from pygments.formatters import HtmlFormatter

        source = highlight(source, HtmlDjangoLexer(), HtmlFormatter())
        source = mark_safe(source)
        source.pygmentized = True
    except ImportError:
        pass

    return render(request, 'debug_toolbar/panels/template_source.html', {
        'source': source,
        'template_name': template_name
    })
