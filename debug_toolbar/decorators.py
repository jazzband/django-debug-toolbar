import functools

from django.http import Http404, HttpResponseBadRequest


def require_show_toolbar(view):
    @functools.wraps(view)
    def inner(request, *args, **kwargs):
        from debug_toolbar.middleware import get_show_toolbar

        show_toolbar = get_show_toolbar()
        if not show_toolbar(request):
            raise Http404

        return view(request, *args, **kwargs)

    return inner


def signed_data_view(view):
    """Decorator that handles unpacking a signed data form"""

    @functools.wraps(view)
    def inner(request, *args, **kwargs):
        from debug_toolbar.forms import SignedDataForm

        data = request.GET if request.method == "GET" else request.POST
        signed_form = SignedDataForm(data)
        if signed_form.is_valid():
            return view(
                request, *args, verified_data=signed_form.verified_data(), **kwargs
            )
        return HttpResponseBadRequest("Invalid signature")

    return inner
