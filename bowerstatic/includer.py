import os
from toposort import topological_sort

class InclusionError(Exception):
    pass


class Includer(object):
    def __init__(self, bower, components_directory, environ):
        self.bower = bower
        self.components_directory = components_directory
        self.environ = environ

    def __call__(self, path_or_resource):
        resource = self.components_directory.get_resource(path_or_resource)
        self.add(ResourceInclusion(resource))

    def add(self, inclusion):
        inclusions = self.environ.setdefault(
            'bowerstatic.inclusions', Inclusions())
        inclusions.add(inclusion)


class Inclusions(object):
    def __init__(self):
        self._inclusions = []

    def add(self, inclusion):
        self._inclusions.append(inclusion)

    def render(self):
        inclusions = topological_sort(
            self._inclusions, lambda inclusion: inclusion.dependencies())
        snippets = [inclusion.html() for inclusion in inclusions]
        return '\n'.join(snippets)


class Inclusion(object):
    def dependencies(self):
        return []

    def html(self):
        raise NotImplementedError()


class ResourceInclusion(Inclusion):
    def __init__(self, resource):
        self.resource = resource
        self.bower = resource.bower
        self.components_directory = resource.components_directory
        # XXX move this into resource logic
        path = resource.path
        parts = path.split('/', 1)
        if len(parts) == 2:
            package_name, file_path = parts
        else:
            package_name = parts[0]
            file_path = None
        self.package = self.components_directory.get_package(package_name)
        if self.package is None:
            raise InclusionError(
                "Package %s not known in components directory %s (%s)" % (
                    package_name, components_directory.name,
                    components_directory.path))
        if file_path is None:
            file_path = self.package.main
        self.file_path = file_path
        dummy, self.ext = os.path.splitext(file_path)

    def __repr__(self):
        return ('<bowerstatic.includer.ResourceInclusion for %s>' %
                self.resource.path)

    def __eq__(self, other):
        return self.resource is other.resource

    def __ne__(self, other):
        return self.resource is not other.resource

    def url(self):
        parts = [
            self.bower.publisher_signature,
            self.components_directory.name,
            self.package.name,
            self.package.version,
            self.file_path]
        return '/' + '/'.join(parts)

    def dependencies(self):
        return [ResourceInclusion(resource)
                for resource in self.resource.dependencies]

    def html(self):
        # XXX should this be based on mimetype instead?
        url = self.url()
        if self.ext == '.js':
            return '<script type="text/javascript" src="%s"></script>' % url
        elif self.ext == '.css':
            return '<link rel="stylesheet" type="text/css" href="%s" />' % url
        assert False, "Unknown extension for url:" % url
