import bowerstatic
from webtest import TestApp as Client
import os
import pytest
from bowerstatic.publisher import FOREVER
from datetime import datetime, timedelta


@pytest.fixture(scope='module')
def c():
    bower = bowerstatic.Bower()

    bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'Hello!']

    publisher = bower.publisher(wsgi)

    return Client(publisher)


def test_publisher_passthrough(c):
    # pass through to underlying WSGI app
    response = c.get('/')
    assert response.body == b'Hello!'


def test_publisher_serve_files(c):
    response = c.get(
        '/bowerstatic/components/jquery/2.1.1/dist/jquery.js')
    assert response.body == b'/* jquery.js 2.1.1 */\n'
    assert response.cache_control.max_age == FOREVER
    utc = response.expires.tzinfo  # get UTC as a hack
    # the test has just run and took less than a full day to run
    # we therefore expect expired to be greater than one_day_ago + FOREVER
    future = datetime.now(utc) - timedelta(days=1) + timedelta(seconds=FOREVER)
    assert response.expires >= future

    response = c.get(
        '/bowerstatic/components/jquery-ui/1.10.4/ui/jquery-ui.js')
    assert response.body == b'/* jquery-ui.js 1.10.4 */\n'


def test_publisher_404_on_publisher_signature(c):
    # a bunch of expected 404s
    c.get('/bowerstatic', status=404)


def test_publisher_404_on_bower_components(c):
    c.get('/bowerstatic/components', status=404)


def test_publisher_404_on_nonexistent_bower_components(c):
    c.get('/bowerstatic/nonexistent_components', status=404)


def test_publisher_404_on_package(c):
    c.get('/bowerstatic/components/jquery', status=404)


def test_publisher_404_on_nonexistent_version(c):
    c.get('/bowerstatic/components/jquery/2.1.0', status=404)


def test_publisher_404_on_version(c):
    c.get('/bowerstatic/components/jquery/2.1.1', status=404)


def test_publisher_404_on_nonexistent_file(c):
    c.get('/bowerstatic/components/jquery/2.1.1/dist/nonexistent.js',
          status=404)


def test_publisher_no_sneaky_escape(c):
    c.get('/bowerstatic/components/jquery/2.1.1/../../../publisher.py',
          status=404)


def test_different_publisher_signature():
    bower = bowerstatic.Bower(publisher_signature='static')

    bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [b'Hello!']

    publisher = bower.publisher(wsgi)

    c = Client(publisher)
    response = c.get('/')
    assert response.body == b'Hello!'
    response = c.get(
        '/static/components/jquery/2.1.1/dist/jquery.js')
    assert response.body == b'/* jquery.js 2.1.1 */\n'


def test_create_directory_with_name_twice():
    # XXX
    pass
