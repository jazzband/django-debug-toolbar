def simple_middleware(get_response):
    def middleware(request):
        return get_response(request)
    return middleware
