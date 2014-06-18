import os
import json
from .publisher import Publisher
from .injector import Injector
from .includer import Includer


class Bower(object):
    """Contains a bunch of bower_components directories.
    """
    def __init__(self, publisher_signature='bowerstatic'):
        self.publisher_signature = publisher_signature
        self._components_directories = {}

    def add(self, name, path):
        self._components_directories[name] = ComponentsDirectory(name, path)

    def middleware(self, wsgi):
        return self.publisher(self.injector(wsgi))

    def publisher(self, wsgi):
        return Publisher(self, wsgi)

    def injector(self, wsgi):
        return Injector(self, wsgi)

    def includer(self, name):
        return self._components_directories[name].includer(self)

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
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self._packages = load_packages(path)

    def includer(self, bower):
        return Includer(bower, self)

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
    return Package(data['name'],
                   data['version'],
                   path)


class Package(object):
    def __init__(self, name, version, path):
        self.name = name
        self.version = version
        self.path = path

    def get_filename(self, version, file_path):
        if version != self.version:
            return None
        filename = os.path.abspath(os.path.join(self.path, file_path))
        # sanity check to prevent file_path to escape from path
        if not filename.startswith(self.path):
            return None
        return filename


