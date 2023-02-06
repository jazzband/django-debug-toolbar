import functools

from django.http import Http404
from django.utils.translation import get_language, override as language_override

from debug_toolbar import settings as dt_settings


def require_show_toolbar(view):
    @functools.wraps(view)
    def inner(request, *args, **kwargs):
        from debug_toolbar.middleware import get_show_toolbar

        show_toolbar = get_show_toolbar()
        if not show_toolbar(request):
            raise Http404

        return view(request, *args, **kwargs)

    return inner


def render_with_toolbar_language(view):
    """Force any rendering within the view to use the toolbar's language."""

    @functools.wraps(view)
    def inner(request, *args, **kwargs):
        lang = dt_settings.get_config()["TOOLBAR_LANGUAGE"] or get_language()
        with language_override(lang):
            return view(request, *args, **kwargs)

    return inner
