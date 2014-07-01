import bowerstatic
from webtest import TestApp as Client
import os
import pytest


@pytest.mark.xfail
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

@pytest.mark.xfail
def test_local_with_local_component():
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

    response = c.get('/bowerstatic/local/local_component/local.js')
    assert response.body == b'/* jquery.js 2.1.1 */\n'
