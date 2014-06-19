import os
import json
from .publisher import Publisher
from .injector import Injector
from .includer import Includer

class Error(Exception):
    pass

class Bower(object):
    """Contains a bunch of bower_components directories.
    """
    def __init__(self, publisher_signature='bowerstatic'):
        self.publisher_signature = publisher_signature
        self._components_directories = {}

    def directory(self, name, path):
        if name in self._components_directories:
            raise Error("Duplicate name for components directory: %s" % name)
        result = ComponentsDirectory(self, name, path)
        self._components_directories[name] = result
        return result

    def wrap(self, wsgi):
        return self.publisher(self.injector(wsgi))

    def publisher(self, wsgi):
        return Publisher(self, wsgi)

    def injector(self, wsgi):
        return Injector(self, wsgi)

    def get_filename(self, bower_components_name,
                     package_name, package_version, file_path):
        components_directory = self._components_directories.get(
            bower_components_name)
        if components_directory is None:
            return None
        return components_directory.get_filename(package_name,
                                                 package_version,
                                                 file_path)


class ComponentsDirectory(object):
    def __init__(self, bower, name, path):
        self.bower = bower
        self.name = name
        self.path = path
        self._packages = load_packages(path)
        self._resources = {}

    def includer(self, environ):
        return Includer(self.bower, self, environ)

    def resource(self, path, dependencies=None):
        dependencies = dependencies or []
        if path in self._resources:
            raise Error("Duplicate path for resource: %s" % path)
        result = Resource(self.bower, self, path, dependencies)
        self._resources[path] = result
        return result

    def get_resource(self, path_or_resource):
        if isinstance(path_or_resource, basestring):
            resource = self._resources.get(path_or_resource)
            if resource is None:
                resource = self.resource(path_or_resource)
        else:
            resource = path_or_resource
            assert resource.components_directory is self
        return resource

    def get_package(self, package_name):
        return self._packages.get(package_name)

    def get_filename(self, package_name, package_version, file_path):
        package = self._packages.get(package_name)
        if package is None:
            return None
        return package.get_filename(package_version, file_path)


def load_packages(path):
    result = {}
    for package_path in os.listdir(path):
        fullpath = os.path.join(path, package_path)
        if not os.path.isdir(fullpath):
            continue
        package = load_package(fullpath)
        result[package.name] = package
    return result


def load_package(path):
    bower_json_filename = os.path.join(path, 'bower.json')
    if not os.path.isfile(bower_json_filename):
        bower_json_filename = os.path.join(path, 'component.json')
    with open(bower_json_filename, 'rb') as f:
        data = json.load(f)
    if isinstance(data['main'], list):
        main = data['main'][0]
    else:
        main = data['main']
    dependencies = data.get('dependencies')
    if dependencies is None:
        dependencies = []
    return Package(path,
                   data['name'],
                   data['version'],
                   main,
                   dependencies)


class Package(object):
    def __init__(self, path, name, version, main, dependencies):
        self.path = path
        self.name = name
        self.version = version
        self.main = main
        self.dependencies = dependencies

    def get_filename(self, version, file_path):
        if version != self.version:
            return None
        filename = os.path.abspath(os.path.join(self.path, file_path))
        # sanity check to prevent file_path to escape from path
        if not filename.startswith(self.path):
            return None
        return filename


class Resource(object):
    def __init__(self, bower, components_directory, path, dependencies):
        self.bower = bower
        self.components_directory = components_directory
        self.path = path
        self.dependencies = [components_directory.get_resource(dependency) for
                             dependency in dependencies]
