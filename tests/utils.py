def get_request_generator(version):
    if version == 1:
        return request_generator()
    elif version == 2:
        return request_generator_2()
    elif version == 3:
        return request_generator_3()

def request_generator():
    yield '<head>'
    yield '<body>'
    for i in xrange(1,100):
        yield '%d<br>' % i
    yield '</body>'
    yield '</head>'

def request_generator_2():
    yield '<head>'
    for i in xrange(1,100):
        yield '%d<br>' % i
    yield '</head>'

def request_generator_3():
    yield '<head>'
    yield '<body>'
    for i in xrange(1,100):
        yield '%d<br>' % i
    yield '</bo'
    yield 'dy>'
    yield '</head>'
