Tips
====

Performance considerations
--------------------------

The Debug Toolbar adds some overhead to the rendering of each page. Depending
on your project, this overhead may slow down page loads significantly. If that
makes development impractical, you can disable the most expensive features to
restore decent response times.

The SQL panel may be the culprit if your view performs many SQL queries. You
should attempt to minimize the number of SQL queries, but this isn't always
possible, for instance if you're using a CMS and have turned off caching for
development. In that case, setting ``ENABLE_STACKTRACES`` to ``False`` in the
``DEBUG_TOOLBAR_CONFIG`` setting will help.

The cache panel is very similar to the SQL panel, except it isn't always a bad
practice to make many cache queries in a view. Setting ``ENABLE_STACKTRACES``
to ``False`` will help there too.

The template panel may be slow if your views or context processors return
large contexts and your templates have complex inheritance or inclusion
schemes. In that case, you should set ``SHOW_TEMPLATE_CONTEXT`` to ``False``
in the ``DEBUG_TOOLBAR_CONFIG`` setting.

If you don't need the panels that are slowing down your application, you can
disable them temporarily by deselecting the checkbox at the top right of each
panel. Depending on implementation details, there may be a residual overhead.
To remove them entirely, you can customize the ``DEBUG_TOOLBAR_PANELS``
setting to include only the panels you actually use.
