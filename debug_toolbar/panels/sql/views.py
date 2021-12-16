from django.http import HttpResponseBadRequest, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from debug_toolbar.decorators import require_show_toolbar, signed_data_view
from debug_toolbar.panels.sql.forms import SQLSelectForm


@csrf_exempt
@require_show_toolbar
@signed_data_view
def sql_select(request, verified_data):
    """Returns the output of the SQL SELECT statement"""
    form = SQLSelectForm(verified_data)

    if form.is_valid():
        sql = form.cleaned_data["raw_sql"]
        params = form.cleaned_data["params"]
        with form.cursor as cursor:
            cursor.execute(sql, params)
            headers = [d[0] for d in cursor.description]
            result = cursor.fetchall()

        context = {
            "result": result,
            "sql": form.reformat_sql(),
            "duration": form.cleaned_data["duration"],
            "headers": headers,
            "alias": form.cleaned_data["alias"],
        }
        content = render_to_string("debug_toolbar/panels/sql_select.html", context)
        return JsonResponse({"content": content})
    return HttpResponseBadRequest("Form errors")


@csrf_exempt
@require_show_toolbar
@signed_data_view
def sql_explain(request, verified_data):
    """Returns the output of the SQL EXPLAIN on the given query"""
    form = SQLSelectForm(verified_data)

    if form.is_valid():
        sql = form.cleaned_data["raw_sql"]
        params = form.cleaned_data["params"]
        vendor = form.connection.vendor
        with form.cursor as cursor:
            if vendor == "sqlite":
                # SQLite's EXPLAIN dumps the low-level opcodes generated for a query;
                # EXPLAIN QUERY PLAN dumps a more human-readable summary
                # See https://www.sqlite.org/lang_explain.html for details
                cursor.execute(f"EXPLAIN QUERY PLAN {sql}", params)
            elif vendor == "postgresql":
                cursor.execute(f"EXPLAIN ANALYZE {sql}", params)
            else:
                cursor.execute(f"EXPLAIN {sql}", params)
            headers = [d[0] for d in cursor.description]
            result = cursor.fetchall()

        context = {
            "result": result,
            "sql": form.reformat_sql(),
            "duration": form.cleaned_data["duration"],
            "headers": headers,
            "alias": form.cleaned_data["alias"],
        }
        content = render_to_string("debug_toolbar/panels/sql_explain.html", context)
        return JsonResponse({"content": content})
    return HttpResponseBadRequest("Form errors")


@csrf_exempt
@require_show_toolbar
@signed_data_view
def sql_profile(request, verified_data):
    """Returns the output of running the SQL and getting the profiling statistics"""
    form = SQLSelectForm(verified_data)

    if form.is_valid():
        sql = form.cleaned_data["raw_sql"]
        params = form.cleaned_data["params"]
        result = None
        headers = None
        result_error = None
        with form.cursor as cursor:
            try:
                cursor.execute("SET PROFILING=1")  # Enable profiling
                cursor.execute(sql, params)  # Execute SELECT
                cursor.execute("SET PROFILING=0")  # Disable profiling
                # The Query ID should always be 1 here but I'll subselect to get
                # the last one just in case...
                cursor.execute(
                    """
                    SELECT *
                    FROM information_schema.profiling
                    WHERE query_id = (
                        SELECT query_id
                        FROM information_schema.profiling
                        ORDER BY query_id DESC
                        LIMIT 1
                    )
                    """
                )
                headers = [d[0] for d in cursor.description]
                result = cursor.fetchall()
            except Exception:
                result_error = (
                    "Profiling is either not available or not supported by your "
                    "database."
                )

        context = {
            "result": result,
            "result_error": result_error,
            "sql": form.reformat_sql(),
            "duration": form.cleaned_data["duration"],
            "headers": headers,
            "alias": form.cleaned_data["alias"],
        }
        content = render_to_string("debug_toolbar/panels/sql_profile.html", context)
        return JsonResponse({"content": content})
    return HttpResponseBadRequest("Form errors")
