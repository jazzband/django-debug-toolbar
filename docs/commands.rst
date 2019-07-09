Commands
========

The Debug Toolbar currently provides one Django management command.

``debugsqlshell``
-----------------

This command starts an interactive Python shell, like Django's built-in
``shell`` management command. In addition, each ORM call that results in a
database query will be beautifully output in the shell.

Here's an example::

    >>> from page.models import Page
    >>> ### Lookup and use resulting in an extra query...
    >>> p = Page.objects.get(pk=1)
    SELECT "page_page"."id",
           "page_page"."number",
           "page_page"."template_id",
           "page_page"."description"
    FROM "page_page"
    WHERE "page_page"."id" = 1

    >>> print(p.template.name)
    SELECT "page_template"."id",
           "page_template"."name",
           "page_template"."description"
    FROM "page_template"
    WHERE "page_template"."id" = 1

    Home
    >>> ### Using select_related to avoid 2nd database call...
    >>> p = Page.objects.select_related('template').get(pk=1)
    SELECT "page_page"."id",
           "page_page"."number",
           "page_page"."template_id",
           "page_page"."description",
           "page_template"."id",
           "page_template"."name",
           "page_template"."description"
    FROM "page_page"
    INNER JOIN "page_template" ON ("page_page"."template_id" = "page_template"."id")
    WHERE "page_page"."id" = 1

    >>> print(p.template.name)
    Home
