import bowerstatic
from webtest import TestApp as Client
import os
import pytest
import json


def test_injector_specific_path():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
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
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</script></head><body>Hello!</body></html>')


def test_injector_specific_path_wrong_file():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        with pytest.raises(bowerstatic.Error):
            include('jquery/nonexistent.js')
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    c.get('/')


def test_injector_specific_path_wrong_file_then_added(tmpdir):
    bower_components_dir = tmpdir.mkdir('bower_components')
    component_dir = bower_components_dir.mkdir('component')
    bower_json_file = component_dir.join('.bower.json')
    bower_json_file.write(json.dumps({
        'name': 'component',
        'version': '2.1',
        'main': 'main.js'
    }))
    main_js_file = component_dir.join('main.js')
    main_js_file.write('/* this is main.js */')

    bower = bowerstatic.Bower()

    components = bower.components('components', bower_components_dir.strpath)

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('component/notyet.js')
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    with pytest.raises(bowerstatic.Error):
        c.get('/')

    # now we add the nonexistent file
    notyet_file = component_dir.join('notyet.js')

    notyet_file.write('/* this is notyet.js */')

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/component/2.1/notyet.js">'
        b'</script></head><body>Hello!</body></html>')


def test_injector_wrong_component():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        with pytest.raises(bowerstatic.Error):
            include('nonexistent/nonexistent.js')
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    c.get('/')


@pytest.mark.xfail
def test_injector_wrong_component_then_added(tmpdir):
    bower_components_dir = tmpdir.mkdir('bower_components')

    bower = bowerstatic.Bower()

    components = bower.components('components', bower_components_dir.strpath)

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('component/main.js')
        return ['<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    with pytest.raises(bowerstatic.Error):
        c.get('/')

    # now add the component
    component_dir = bower_components_dir.mkdir('component')
    bower_json_file = component_dir.join('.bower.json')
    bower_json_file.write(json.dumps({
        'name': 'component',
        'version': '2.1',
        'main': 'main.js'
    }))
    main_js_file = component_dir.join('main.js')
    main_js_file.write('/* this is main.js */')

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/component/2.1/main.js">'
        b'</script></head><body>Hello!</body></html>')



def test_injector_specific_resource():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
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
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</script></head><body>Hello!</body></html>')


def test_injector_endpoint_path():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
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
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</script></head><body>Hello!</body></html>')


def test_injector_endpoint_resource():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
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
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</script></head><body>Hello!</body></html>')


def test_injector_endpoint_dependencies():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
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

    components = bower.components('components', os.path.join(
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

    components = bower.components('components', os.path.join(
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

    components = bower.components('components', os.path.join(
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

    bower.components('components', os.path.join(
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

    components = bower.components('components', os.path.join(
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

    components = bower.components('components', os.path.join(
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

    components = bower.components('components', os.path.join(
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
