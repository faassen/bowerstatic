import os


class Includer(object):
    def __init__(self, bower, components_directory):
        self.bower = bower
        self.components_directory = components_directory

    def __call__(self, environ, package_name, path=None):
        self.add(environ, Inclusion(self.bower, self.components_directory,
                                    package_name, path))

    def add(self, environ, inclusion):
        inclusions = environ.setdefault('bowerstatic.inclusions', Inclusions())
        inclusions.add(inclusion)


class Inclusions(object):
    def __init__(self):
        self._inclusions = []

    def add(self, inclusion):
        self._inclusions.append(inclusion)

    def render(self):
        snippets = [inclusion.html() for inclusion in self._inclusions]
        return '\n'.join(snippets)


class InclusionError(Exception):
    pass


class Inclusion(object):
    def __init__(self, bower, components_directory, package_name, path):
        self.bower = bower
        self.components_directory = components_directory
        self.package = self.components_directory.get_package(package_name)
        if self.package is None:
            raise InclusionError(
                "Package %s not known in components directory %s (%s)" % (
                    package_name, components_directory.name,
                    components_directory.path))
        self.path = path
        dummy, self.ext = os.path.splitext(path)

    def url(self):
        parts = [
            self.bower.publisher_signature,
            self.components_directory.name,
            self.package.name,
            self.package.version,
            self.path]
        return '/' + '/'.join(parts)

    def html(self):
        # XXX should this be based on mimetype instead?
        url = self.url()
        if self.ext == '.js':
            return '<script type="text/javascript" src="%s"></script>' % url
        elif self.ext == '.css':
            return '<link rel="stylesheet" type="text/css" href="%s" />' % url
        assert False, "Unknown extension for url:" % url
