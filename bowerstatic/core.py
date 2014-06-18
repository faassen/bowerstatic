#
class Bower(object):
    """Contains a bunch of bower_components directories.
    """
    def __init__(self):
        self._directories = {}

    def add(self, name, path):
        self._directories[name] = BowerComponents(name, path)

    def publisher(self, wsgi):
        return Publisher(self, wsgi)

    def injector(self, wsgi):
        return Injector(self, wsgi)

    def includer(self, name):
        return self._directories[name].includer()


class BowerComponents(object):
    def __init__(self, name, path):
        pass

    def includer(self):
        return Includer(self)

class Package(object):
    def __init__(self, name):
        pass

class Resource(object):
    def __init__(self, name, path):
        pass


class Publisher(object):
    def __init__(self, bower, wsgi):
        pass

class Injector(object):
    def __init__(self, bower, wsgi):
        pass

class Includer(object):
    def __init__(self, bower_components):
        pass

    def __call__(self, path=None):
        pass
