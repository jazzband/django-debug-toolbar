from django.core.cache import cache


class UseCacheAfterToolbar:
    """
    This middleware exists to use the cache before and after
    the toolbar is setup.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        cache.set("UseCacheAfterToolbar.before", 1)
        response = self.get_response(request)
        cache.set("UseCacheAfterToolbar.after", 1)
        return response
