

class SimpleOrigin(object):
    name = None

    def __init__(self, name):
        self.name = name

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return self.name
