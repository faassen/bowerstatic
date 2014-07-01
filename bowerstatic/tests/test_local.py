import bowerstatic
from webtest import TestApp as Client
import os
import pytest


def test_local_falls_back_to_components():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    local = bower.local_components('local', components)

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = local.includer(environ)
        include('jquery/dist/jquery.js')
        return ['<html><head></head><body>Hello!</body></html>']

    wrapped = bower.wrap(wsgi)

    c = Client(wrapped)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</script></head><body>Hello!</body></html>')

    response = c.get('/bowerstatic/components/jquery/2.1.1/dist/jquery.js')
    assert response.body == b'/* jquery.js 2.1.1 */\n'


def test_local_with_local_component_main():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    local = bower.local_components('local', components)

    path = os.path.join(
        os.path.dirname(__file__), 'local_component')

    local.component(path, version='2.0')

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = local.includer(environ)
        include('local_component')
        return ['<html><head></head><body>Hello!</body></html>']

    wrapped = bower.wrap(wsgi)

    c = Client(wrapped)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/local/local_component/2.0/local.js">'
        b'</script></head><body>Hello!</body></html>')

    response = c.get('/bowerstatic/local/local_component/2.0/local.js')
    assert response.body == b'/* this is local.js */\n'


def test_local_with_local_component_specific_file():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    local = bower.local_components('local', components)

    path = os.path.join(
        os.path.dirname(__file__), 'local_component')

    local.component(path, version='2.0')

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = local.includer(environ)
        include('local_component/local.js')
        return ['<html><head></head><body>Hello!</body></html>']

    wrapped = bower.wrap(wsgi)

    c = Client(wrapped)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/local/local_component/2.0/local.js">'
        b'</script></head><body>Hello!</body></html>')

    response = c.get('/bowerstatic/local/local_component/2.0/local.js')
    assert response.body == b'/* this is local.js */\n'


def test_local_internal_dependencies():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    local = bower.local_components('local', components)

    path = os.path.join(
        os.path.dirname(__file__), 'local_component')

    local.component(path, version='2.0')

    local.resource('local_component/second.js', dependencies=[
        'local_component/local.js'])

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = local.includer(environ)
        include('local_component/second.js')
        return ['<html><head></head><body>Hello!</body></html>']

    wrapped = bower.wrap(wsgi)

    c = Client(wrapped)

    response = c.get('/')

    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/local/local_component/2.0/local.js"></script>\n'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/local/local_component/2.0/second.js"></script>'
        b'</head><body>Hello!</body></html>')


def test_local__external_dependencies():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    local = bower.local_components('local', components)

    path = os.path.join(
        os.path.dirname(__file__), 'local_component')

    local.component(path, version='2.0')

    local.resource('local_component/local.js', dependencies=[
        'jquery'])

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = local.includer(environ)
        include('local_component/local.js')
        return ['<html><head></head><body>Hello!</body></html>']

    wrapped = bower.wrap(wsgi)

    c = Client(wrapped)

    response = c.get('/')

    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</script>\n'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/local/local_component/2.0/local.js"></script>'
        b'</head><body>Hello!</body></html>')


def test_local_bower_json_dependencies():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    local = bower.local_components('local', components)

    path = os.path.join(
        os.path.dirname(__file__), 'local_component_deps')

    local.component(path, version='2.0')

    local.resource('local_component/local.js', dependencies=[
        'jquery'])

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = local.includer(environ)
        include('local_component/local.js')
        return ['<html><head></head><body>Hello!</body></html>']

    wrapped = bower.wrap(wsgi)

    c = Client(wrapped)

    response = c.get('/')

    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</script>\n'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/local/local_component/2.0/local.js"></script>'
        b'</head><body>Hello!</body></html>')

