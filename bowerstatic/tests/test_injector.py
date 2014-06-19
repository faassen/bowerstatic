import bowerstatic
from webtest import TestApp as Client
import os


def test_injector():
    bower = bowerstatic.Bower()

    bower.add('bower_components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = bower.includer(environ, 'bower_components')
        include('jquery', 'dist/jquery.js')
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        '<script type="text/javascript" '
        'src="/bowerstatic/bower_components/jquery/2.1.1/dist/jquery.js">'
        '</script></head><body>Hello!</body></html>')


def test_injector_no_inclusions():
    bower = bowerstatic.Bower()

    bower.add('bower_components', os.path.join(
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

    bower.add('bower_components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = bower.includer(environ, 'bower_components')
        include('jquery', 'dist/jquery.js')
        return ['<html><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == b'<html><body>Hello!</body></html>'


def test_injector_not_html_no_effect():
    bower = bowerstatic.Bower()

    bower.add('bower_components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        include = bower.includer(environ, 'bower_components')
        include('jquery', 'dist/jquery.js')
        return ['Hello!']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == b'Hello!'


def test_injector_PUT_no_effect():
    bower = bowerstatic.Bower()

    bower.add('bower_components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = bower.includer(environ, 'bower_components')
        include('jquery', 'dist/jquery.js')
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.put('/')
    assert response.body == b'<html><head></head><body>Hello!</body></html>'
