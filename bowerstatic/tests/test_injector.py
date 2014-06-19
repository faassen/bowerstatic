import bowerstatic
from webtest import TestApp as Client
import os
import pytest


def test_injector_specific_path():
    bower = bowerstatic.Bower()

    components = bower.directory('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery/dist/jquery.js')
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        '<script type="text/javascript" '
        'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        '</script></head><body>Hello!</body></html>')


def test_injector_specific_resource():
    bower = bowerstatic.Bower()

    components = bower.directory('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    jquery = components.resource('jquery/dist/jquery.js')

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include(jquery)
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        '<script type="text/javascript" '
        'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        '</script></head><body>Hello!</body></html>')


def test_injector_endpoint_path():
    bower = bowerstatic.Bower()

    components = bower.directory('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery')
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        '<script type="text/javascript" '
        'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        '</script></head><body>Hello!</body></html>')


def test_injector_endpoint_resource():
    bower = bowerstatic.Bower()

    components = bower.directory('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    jquery = components.resource('jquery')

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include(jquery)
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        '<script type="text/javascript" '
        'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        '</script></head><body>Hello!</body></html>')


def test_injector_endpoint_dependencies():
    bower = bowerstatic.Bower()

    components = bower.directory('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery-ui')
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</script>\n'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery-ui/'
        b'1.10.4/ui/jquery-ui.js">'
        b'</script>'
        b'</head><body>Hello!</body></html>')


def test_injector_endpoint_dependencies_with_explicit_resource_objects():
    bower = bowerstatic.Bower()

    components = bower.directory('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    jquery_ui = components.resource('jquery-ui')

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include(jquery_ui)
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</script>\n'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery-ui/'
        b'1.10.4/ui/jquery-ui.js">'
        b'</script>'
        b'</head><body>Hello!</body></html>')


def test_injector_normal_dependencies():
    bower = bowerstatic.Bower()

    components = bower.directory('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    components.resource(
        'jquery-ui/ui/minified/jquery-ui.min.js',
        dependencies=['jquery/dist/jquery.min.js'])

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery-ui/ui/minified/jquery-ui.min.js')
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.min.js">'
        b'</script>\n'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery-ui/'
        b'1.10.4/ui/minified/jquery-ui.min.js">'
        b'</script>'
        b'</head><body>Hello!</body></html>')


def test_injector_normal_dependencies_explicit_resource_objects():
    bower = bowerstatic.Bower()

    components = bower.directory('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    jquery_min = components.resource(
        'jquery/dist/jquery.min.js')

    jquery_ui_min = components.resource(
        'jquery-ui/ui/minified/jquery-ui.min.js',
        dependencies=[jquery_min])

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include(jquery_ui_min)
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.min.js">'
        b'</script>\n'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery-ui/'
        b'1.10.4/ui/minified/jquery-ui.min.js">'
        b'</script>'
        b'</head><body>Hello!</body></html>')


def test_injector_no_inclusions():
    bower = bowerstatic.Bower()

    bower.directory('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == b'<html><head></head><body>Hello!</body></html>'


def test_injector_no_head_to_inject():
    bower = bowerstatic.Bower()

    components = bower.directory('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery/dist/jquery.js')
        return ['<html><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == b'<html><body>Hello!</body></html>'


def test_injector_not_html_no_effect():
    bower = bowerstatic.Bower()

    components = bower.directory('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        include = components.includer(environ)
        include('jquery/dist/jquery.js')
        return ['Hello!']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == b'Hello!'


def test_injector_PUT_no_effect():
    bower = bowerstatic.Bower()

    components = bower.directory('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery/dist/jquery.js')
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.put('/')
    assert response.body == b'<html><head></head><body>Hello!</body></html>'
