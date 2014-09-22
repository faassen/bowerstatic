from webtest import TestApp as Client
import bowerstatic
import os
import pytest


def test_wrap():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
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


def test_component_url():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    assert (components.get_component('jquery').url() ==
            '/bowerstatic/components/jquery/2.1.1/')


def test_component_url_local():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    local = bower.local_components('local', components)

    assert (local.get_component('jquery').url() ==
            '/bowerstatic/components/jquery/2.1.1/')


def test_nice_error_message_when_depending_on_not_existing_dependency():
    bower = bowerstatic.Bower()

    with pytest.raises(bowerstatic.error.Error) as excinfo:
        bower.components('components', os.path.join(
            os.path.dirname(__file__), 'bower_components_error'))
    assert "Component u'i-do-not-exist' missing." == str(excinfo.value)
