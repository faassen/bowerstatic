import os
import json
from .publisher import Publisher
from .injector import Injector
from .includer import Includer
from .autoversion import autoversion
from .error import Error


class Bower(object):
    """Contains a bunch of bower_components directories.
    """
    def __init__(self, publisher_signature='bowerstatic'):
        self.publisher_signature = publisher_signature
        self._component_collections = {}

    def components(self, name, path):
        if name in self._component_collections:
            raise Error("Duplicate name for components directory: %s" % name)
        result = ComponentCollection(self, name, load_components(path))
        self._component_collections[name] = result
        return result

    def local_components(self, name, component_collection):
        if name in self._component_collections:
            raise Error("Duplicate name for local components: %s" % name)
        result = LocalComponentCollection(self, name, component_collection)
        self._component_collections[name] = result
        return result

    def wrap(self, wsgi):
        return self.publisher(self.injector(wsgi))

    def publisher(self, wsgi):
        return Publisher(self, wsgi)

    def injector(self, wsgi):
        return Injector(self, wsgi)

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
    def __init__(self, bower, name, components):
        self.bower = bower
        self.name = name
        self._components = components
        self._resources = {}
        for component in components.values():
            component.create_main_resource(self)

    def add(self, component, component_collection=None):
        self._components[component.name] = component
        component_collection = component_collection or self
        component.create_main_resource(component_collection)

    def includer(self, environ):
        return Includer(self.bower, self, environ)

    def resource(self, path, dependencies=None, component_collection=None):
        resource = self._resources.get(path)
        if resource is not None:
            return resource
        component_collection = component_collection or self
        dependencies = dependencies or []
        result = create_resources(self.bower, component_collection,
                                  path, dependencies)
        if result is None:
            return None
        if not result:
            return None
        result = result[0]
        self._resources[path] = result
        return result

    def get_resource(self, path):
        return self._resources.get(path)

    def path_to_resources(self, path_or_resource):
        if isinstance(path_or_resource, basestring):
            resource = self.resource(path_or_resource, [])
        else:
            resource = path_or_resource
        if resource is None:
            return None
        return [resource]

    def get_component(self, component_name):
        return self._components.get(component_name)

    def get_filename(self, component_name, component_version, file_path):
        component = self._components.get(component_name)
        if component is None:
            return None
        return component.get_filename(component_version, file_path)


class LocalComponentCollection(object):
    def __init__(self, bower, name, component_collection):
        self.bower = bower
        self.name = name
        self.local_collection = ComponentCollection(bower, name, {})
        self.component_collection = component_collection

    def includer(self, environ):
        return Includer(self.bower, self, environ)

    def resource(self, path, dependencies=None):
        dependencies = dependencies or []
        result = self.local_collection.resource(path, dependencies, self)
        if result is not None:
            return result
        return self.component_collection.resource(path, dependencies)

    def component(self, path, version):
        self.local_collection.add(
            load_component(path, 'bower.json', version, version is None), self)

    def get_resource(self, path):
        result = self.local_collection.get_resource(path)
        if result is not None:
            return result
        return self.component_collection.get_resource(path)

    def path_to_resources(self, path_or_resource):
        result = self.local_collection.path_to_resources(path_or_resource)
        if result is not None:
            return result
        return self.component_collection.path_to_resources(path_or_resource)

    def get_component(self, component_name):
        result = self.local_collection.get_component(component_name)
        if result is not None:
            return result
        return self.component_collection.get_component(component_name)

    def get_filename(self, component_name, component_version, file_path):
        result = self.local_collection.get_filename(
            component_name, component_version, file_path)
        if result is not None:
            return result
        return self.component_collection.get_filename(
            component_name, component_version, file_path)


def load_components(path):
    result = {}
    for component_path in os.listdir(path):
        fullpath = os.path.join(path, component_path)
        if not os.path.isdir(fullpath):
            continue
        component = load_component(fullpath, '.bower.json')
        if component is None:
            continue
        result[component.name] = component
    return result


def load_component(path, bower_filename, version=None, autoversion=False):
    bower_json_filename = os.path.join(path, bower_filename)
    with open(bower_json_filename, 'rb') as f:
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
    version = version or data['version']
    return Component(path,
                     data['name'],
                     version,
                     main,
                     dependencies,
                     autoversion=autoversion)


class Component(object):
    def __init__(self, path, name, version, main, dependencies, autoversion):
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
        return autoversion(self.path)

    def create_main_resource(self, component_collection):
        # if the resource was already created, return it
        resource = component_collection.get_resource(self.name)
        if resource is not None:
            return resource
        # create a main resource for all dependencies
        dependencies = []
        for component_name in self.dependencies.keys():
            component = component_collection.get_component(component_name)
            dependencies.append(
                component.create_main_resource(component_collection))
        # depend on those main resources in this resource
        return component_collection.resource(
            self.name, dependencies=dependencies)

    def get_filename(self, version, file_path):
        if version != self.version:
            return None
        filename = os.path.abspath(os.path.join(self.path, file_path))
        # sanity check to prevent file_path to escape from path
        if not filename.startswith(self.path):
            return None
        return filename


def get_component_and_filepaths(component_collection, path):
    parts = path.split('/', 1)
    if len(parts) == 2:
        component_name, file_path = parts
    else:
        component_name = parts[0]
        file_path = None
    component = component_collection.get_component(component_name)
    if component is None:
        return None
    if file_path is None:
        file_paths = component.main
    else:
        file_paths = [file_path]
    for file_path in file_paths:
        full_path = os.path.join(component.path, file_path)
        if not os.path.exists(full_path):
            raise Error("resource path %s - cannot find resource file: %s" %
                        (path, full_path))
    return component, file_paths


def create_resources(bower, component_collection, path, dependencies):
    info = get_component_and_filepaths(component_collection, path)
    if info is None:
        return None
    component, file_paths = info
    dependency_resources = []
    for dependency in dependencies:
        dependency_resources.extend(
            component_collection.path_to_resources(dependency))
    return [Resource(bower, component_collection, component,
                     file_path, dependency_resources) for file_path
            in file_paths]


class Resource(object):
    def __init__(self, bower, component_collection,
                 component, file_path, dependencies):
        self.bower = bower
        self.component_collection = component_collection
        self.component = component
        if file_path.startswith('./'):
            file_path = file_path[2:]
        self.file_path = file_path
        self.dependencies = dependencies
        dummy, self.ext = os.path.splitext(file_path)

    def url(self):
        parts = [
            self.bower.publisher_signature,
            self.component_collection.name,
            self.component.name,
            self.component.version,
            self.file_path]
        return '/' + '/'.join(parts)
