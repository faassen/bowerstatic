import os
import json
from . import compat
from .publisher import Publisher
from .injector import Injector
from .includer import Includer
from .autoversion import filesystem_second_autoversion
from .error import Error
from .renderer import Renderer


class Bower(object):
    """Contains a bunch of bower_components directories.
    """
    def __init__(self, publisher_signature='bowerstatic', autoversion=None):
        self.publisher_signature = publisher_signature
        self._component_collections = {}
        self._renderer = Renderer()
        self.autoversion = autoversion or filesystem_second_autoversion

    def components(self, name, path):
        if name in self._component_collections:
            raise Error("Duplicate name for components directory: %s" % name)
        result = ComponentCollection(self, name, path=path)
        self._component_collections[name] = result
        return result

    def local_components(self, name, component_collection):
        if name in self._component_collections:
            raise Error("Duplicate name for local components: %s" % name)
        result = ComponentCollection(self, name,
                                     fallback_collection=component_collection)
        self._component_collections[name] = result
        return result

    def wrap(self, wsgi):
        return self.publisher(self.injector(wsgi))

    def publisher(self, wsgi):
        return Publisher(self, wsgi)

    def injector(self, wsgi):
        return Injector(self, wsgi)

    def register_renderer(self, ext, render_func):
        self._renderer.register(ext, render_func)

    def renderer(self, resource):
        return self._renderer.renderer(resource)

    def filter_by_known_ext(self, paths):
        return self._renderer.filter_by_known_ext(paths)

    def get_filename(self, bower_components_name,
                     component_name, component_version, file_path):
        component_collection = self._component_collections.get(
            bower_components_name)
        if component_collection is None:
            return None
        return component_collection.get_filename(component_name,
                                                 component_version,
                                                 file_path)


class ComponentCollection(object):
    def __init__(self, bower, name, path=None, fallback_collection=None):
        self.bower = bower
        self.name = name
        self._resources = {}
        self.path = path
        self.fallback_collection = fallback_collection
        if path is not None:
            self._components = self.load_components(path)
        else:
            self._components = {}
        for component in self._components.values():
            self.create_main_resources(component)

    def add(self, component):
        self._components[component.name] = component
        self.create_main_resources(component)

    def component(self, path, version):
        assert self.fallback_collection is not None
        component = self.load_component(
            path, 'bower.json', version, version is None)
        self.add(component)
        return component

    def load_components(self, path):
        result = {}
        for component_path in os.listdir(path):
            if component_path.startswith('.'):
                continue
            fullpath = os.path.join(path, component_path)
            if not os.path.isdir(fullpath):
                continue
            component = self.load_component(fullpath, '.bower.json')
            if component is None:
                continue
            result[component.name] = component
        return result

    def load_component(self, path, bower_filename, version=None,
                       autoversion=False):
        bower_json_filename = os.path.join(path, bower_filename)
        with open(bower_json_filename, 'r') as f:
            data = json.load(f)
        if 'main' not in data:
            main = []
        elif isinstance(data['main'], list):
            main = data['main']
        else:
            main = [data['main']]
        dependencies = data.get('dependencies')
        if dependencies is None:
            dependencies = {}
        if not version:
            version = data.get('_release')
        if not version:
            try:
                version = data['version']
            except KeyError:
                raise ValueError('Missing _release and version in {}'.format(
                    path))
        return Component(self.bower,
                         self,
                         path,
                         data['name'],
                         version,
                         main,
                         dependencies,
                         autoversion=autoversion)

    def create_main_resources(self, component):
        # if the resource was already created, return it
        resources = self.get_resources(component.name)
        if resources is not None:
            return resources
        # depend on those main resources in these resources
        return self.resources(
            component.name,
            dependencies=component.dependencies_resources())

    def includer(self, environ):
        return Includer(self.bower, self, environ)

    def resources(self, path, dependencies=None):
        resources = self.get_resources(path)
        if resources is not None:
            return resources
        dependencies = dependencies or []
        result = self.create_resources(path, dependencies)
        if result is None:
            return None
        self._resources[path] = result
        return result

    resource = resources

    def get_resources(self, path):
        result = self._resources.get(path)
        if result is not None:
            return result
        if self.fallback_collection is None:
            return None
        return self.fallback_collection.get_resources(path)

    def path_to_resources(self, path_or_resources):
        if isinstance(path_or_resources, compat.string_types):
            resources = self.resources(path_or_resources, [])
        elif isinstance(path_or_resources, list):
            resources = path_or_resources
        else:
            resources = [path_or_resources]
        if resources is None:
            return None
        return resources

    def get_component(self, component_name):
        result = self._components.get(component_name)
        if result is not None:
            return result
        if self.fallback_collection is None:
            return None
        return self.fallback_collection.get_component(component_name)

    def get_filename(self, component_name, component_version, file_path):
        component = self.get_component(component_name)
        if component is None:
            return None
        return component.get_filename(component_version, file_path)

    def get_component_and_filepaths(self, path):
        parts = path.split('/', 1)
        if len(parts) == 2:
            component_name, file_path = parts
        else:
            component_name = parts[0]
            file_path = None
        component = self.get_component(component_name)
        if component is None:
            return None
        if file_path is None:
            file_paths = self.bower.filter_by_known_ext(component.main)
        else:
            file_paths = [file_path]
        for file_path in file_paths:
            full_path = os.path.join(component.path, file_path)
            if not os.path.exists(full_path):
                raise Error(
                    "resource path %s - cannot find resource file: %s" %
                    (path, full_path))
        return component, file_paths

    def create_resources(self, path, dependencies):
        info = self.get_component_and_filepaths(path)
        if info is None:
            return None
        component, file_paths = info
        dependency_resources = []
        for dependency in dependencies:
            dependency_resources.extend(self.path_to_resources(dependency))
        return [Resource(component, file_path, dependency_resources)
                for file_path in file_paths]


class Component(object):
    def __init__(self, bower, component_collection,
                 path, name, version, main, dependencies, autoversion):
        self.bower = bower
        self.component_collection = component_collection
        self.path = path
        self.name = name
        self._version = version
        self.main = main
        self.dependencies = dependencies
        self.autoversion = autoversion

    @property
    def version(self):
        if not self.autoversion:
            return self._version
        return self.bower.autoversion(self.path)

    def get_filename(self, version, file_path):
        if version != self.version:
            return None
        filename = os.path.abspath(os.path.join(self.path, file_path))
        # sanity check to prevent file_path to escape from path
        if not filename.startswith(self.path):
            return None
        return filename

    def dependencies_resources(self):
        result = []
        for component_name in self.dependencies.keys():
            found_component = self.component_collection.get_component(
                component_name)
            if found_component is None:
                raise Error("Component %s missing." % component_name)
            result.extend(
                found_component.component_collection.create_main_resources(
                    found_component))
        return result

    def url(self):
        parts = [
            self.bower.publisher_signature,
            self.component_collection.name,
            self.name,
            self.version,
        ]
        return '/' + '/'.join(parts) + '/'

    def renderer(self, resource):
        return self.bower.renderer(resource)


class Resource(object):
    def __init__(self, component, file_path, dependencies):
        self.component = component
        if file_path.startswith('./'):
            file_path = file_path[2:]
        self.file_path = file_path
        self.dependencies = dependencies
        dummy, self.ext = os.path.splitext(file_path)

    def url(self):
        return self.component.url() + self.file_path

    def html(self):
        return self.renderer(self)

    def content(self):
        with open(self.component.get_filename(
                self.component.version, self.file_path)) as f:
            return f.read()

    def renderer(self):
        return self.component.renderer(self)
