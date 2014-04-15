

class CustomMiddleware(object):
    def process_request(request):
        request.myattr = 'test attribute'
