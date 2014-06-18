import bowerstatic
from webtest import TestApp as Client
import os
import pytest


@pytest.mark.xfail
def test_dependencies():
    bower = bowerstatic.Bower()

    bower.add('bower_components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    resources = bower.resources('bower_components')

    jquery = resources.get('jquery', 'dist/jquery.min.js')
    jquery_ui = resources.get('jquery-ui', 'ui/minified/jquery-ui.min.js')
    jquery_ui.depends_on(jquery)

    includer = bower.includer('bower_components')

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        includer(environ, 'jquery-ui', 'ui/minified/jquery-ui.min.js')
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == b''
