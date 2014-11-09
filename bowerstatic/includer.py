from .toposort import topological_sort
from .error import Error


class Includer(object):
    def __init__(self, bower, components_directory, environ):
        self.bower = bower
        self.components_directory = components_directory
        self.environ = environ

    def __call__(self, path_or_resources, custom_html=None):
        resources = self.components_directory.path_to_resources(
            path_or_resources)
        if resources is None:
            raise Error("Cannot find component for path (need restart?): %s" %
                        path_or_resources)
        for resource in resources:
            self.add(ResourceInclusion(resource, custom_html))

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
    def __init__(self, resource, custom_html=None):
        self.resource = resource
        self.custom_html = custom_html

    def __repr__(self):
        return ('<bowerstatic.includer.ResourceInclusion for %s>' %
                self.resource.path)

    def __hash__(self):
        return hash(self.resource)

    def __eq__(self, other):
        return self.resource is other.resource

    def __ne__(self, other):
        return self.resource is not other.resource

    def dependencies(self):
        return [ResourceInclusion(resource)
                for resource in self.resource.dependencies]

    def html(self):
        if self.custom_html is not None:
            if isinstance(self.custom_html, basestring):
                # format string
                return self.custom_html.format(url=self.resource.url())
            if callable(self.custom_html):
                return self.custom_html(url=self.resource.url())
            raise ValueError('unknown html renderer')

        return self.resource.html()
