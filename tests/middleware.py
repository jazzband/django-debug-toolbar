def simple_middleware(get_response):
    """
    Used to test Django 1.10 compatibility.
    """
    def middleware(request):
        return get_response(request)
    return middleware
