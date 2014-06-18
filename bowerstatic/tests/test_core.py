import bowerstatic
from webtest import TestApp as Client
import os
import pytest

@pytest.fixture
def c():
    bower = bowerstatic.Bower()

    bower.add('bower_components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Hello!']

    publisher = bower.publisher(wsgi)

    return Client(publisher)


def test_publisher_passthrough(c):
    # pass through to underlying WSGI app
    response = c.get('/')
    assert response.body == b'Hello!'

def test_publisher_serve_files(c):
    # access bowerstatic files
    response = c.get(
        '/bowerstatic/bower_components/jquery/2.1.1/dist/jquery.js')
    assert response.body == b'/* jquery.js 2.1.1 */\n'

    response = c.get(
        '/bowerstatic/bower_components/jquery-ui/1.10.4/ui/jquery-ui.js')
    assert response.body == b'/* jquery-ui.js 1.10.4 */\n'


def test_publisher_404_on_publisher_signature(c):
    # a bunch of expected 404s
    c.get('/bowerstatic', status=404)


def test_publisher_404_on_bower_components(c):
    c.get('/bowerstatic/bower_components', status=404)


def test_publisher_404_on_nonexistent_bower_components(c):
    c.get('/bowerstatic/nonexistent_components', status=404)


def test_publisher_404_on_package(c):
    c.get('/bowerstatic/bower_components/jquery', status=404)


def test_publisher_404_on_nonexistent_version(c):
    c.get('/bowerstatic/bower_components/jquery/2.1.0', status=404)


def test_publisher_404_on_version(c):
    c.get('/bowerstatic/bower_components/jquery/2.1.1', status=404)


def test_publisher_404_on_nonexistent_file(c):
    c.get('/bowerstatic/bower_components/jquery/2.1.1/dist/nonexistent.js',
          status=404)


def test_publisher_no_sneaky_escape(c):
    c.get('/bowerstatic/bower_components/jquery/2.1.1/../../../publisher.py',
          status=404)

# def test_tracer_bullet():
#     bower = bowerstatic.Bower()
#     bower.add('bower_components', 'bower_components')
#     def wsgi(env, start_response):
#         pass
#     publisher = bower.publisher(wsgi)
#     injector = bower.injector(publisher)

#     includer = bower.includer('bower_components')
#     includer()


