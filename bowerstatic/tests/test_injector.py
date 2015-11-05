from webtest import TestApp as Client
import bowerstatic
import json
import mock
import os
import pytest


def test_injector_specific_path():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery/dist/jquery.js')
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    c.get('/')


def test_injector_does_not_fail_for_401_responses_with_no_content_type():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        # Can not use 401 here as webtest only accepts 200 or 3xx, which is ok
        # as we want to test the behaviour if no content type is given
        start_response('302', [('Content-Type', None)])
        include = components.includer(environ)
        with pytest.raises(bowerstatic.Error):
            include('jquery/nonexistent.js')
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    # webtest checks, in contracy to pyramid, the headers and breaks if one of
    # them is not a string.
    with mock.patch('webtest.lint.check_headers'):
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
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</script></head><body>Hello!</body></html>')


def test_injector_endpoint_main_missing():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('missing_main')
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')

    # without a main, it should just include nothing
    assert response.body == (
        b'<html><head></head><body>Hello!</body></html>')


def test_injector_endpoint_depends_on_main_missing():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('depends_on_missing_main')
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')

    # without a main, it should just include nothing
    assert response.body == (
        b'<html><head><script type="text/javascript" '
        b'src="/bowerstatic/components/depends_on_missing_main/'
        b'2.1.1/resource.js"></script></head><body>Hello!</body></html>')


def test_injector_missing_version_bower_components():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('missing-version-in-dot-bower-json')
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')

    # without a main, it should just include nothing
    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/missing-version-in-dot-bower-json/'
        b'1.0/example.js"></script>'
        b'</head><body>Hello!</body></html>')




def test_injector_endpoint_multiple_mains():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('multi_main')
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')

    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/multi_main/2.1.1/dist/jquery.js">'
        b'</script>\n'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/multi_main/2.1.1/dist/another.js">'
        b'</script></head><body>Hello!</body></html>')


def test_injector_endpoint_depends_on_multiple_mains():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('depends_on_multi_main')
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')

    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/multi_main/2.1.1/dist/jquery.js">'
        b'</script>\n'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/multi_main/2.1.1/dist/another.js">'
        b'</script>\n'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/depends_on_multi_main/'
        b'2.1.1/dist/resource.js"></script>'
        b'</head><body>Hello!</body></html>')


def test_injector_endpoint_resource():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    jquery = components.resource('jquery')

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include(jquery)
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == b'<html><head></head><body>Hello!</body></html>'


def test_injector_multiple_identical_inclusions():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery')
        include('jquery')
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')

    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</script></head><body>Hello!</body></html>')


def test_injector_multiple_identical_inclusions_through_dependencies():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        # going to pull in jquery-ui and jquery twice
        include('jquery-ui')
        include('jquery-ui-bootstrap')
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')

    assert response.body == (
        b'<html><head>'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</script>\n'
        b'<script type="text/javascript" '
        b'src="/bowerstatic/components/jquery-ui/1.10.4/ui/jquery-ui.js">'
        b'</script>\n'
        b'<link rel="stylesheet" type="text/css" '
        b'href="/bowerstatic/components/jquery-ui-bootstrap/0.2.5/'
        b'jquery.ui.theme.css">'
        b'</head><body>Hello!</body></html>')


def test_injector_no_head_to_inject():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery/dist/jquery.js')
        return [b'<html><body>Hello!</body></html>']

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
        return [b'Hello!']

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
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.put('/')
    assert response.body == b'<html><head></head><body>Hello!</body></html>'


def test_custom_renderer():
    bower = bowerstatic.Bower()

    def render_foo(resource):
        return '<foo>%s</foo>' % resource.url()

    bower.register_renderer('.foo', render_foo)

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery/dist/resource.foo')
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head><foo>/bowerstatic/components/jquery/2.1.1/dist/'
        b'resource.foo</foo>'
        b'</head><body>Hello!</body></html>')


def test_missing_renderer():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery/dist/resource.foo')
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    with pytest.raises(bowerstatic.Error):
        c.get('/')


def test_injector_main_unknown_extension():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('unknown_ext_in_main')
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')

    assert response.body == (
        b'<html><head><script type="text/javascript" '
        b'src="/bowerstatic/components/unknown_ext_in_main/2.1.1/'
        b'dist/jquery.js"></script></head><body>Hello!</body></html>')


def test_injector_custom_renderer_string_format():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery', '<link src="{url}">')
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        b'<link src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</head><body>Hello!</body></html>')


def test_injector_custom_renderer_callable():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def custom_renderer(resource):
        return '<link src="%s">' % resource.url()

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery', custom_renderer)
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head>'
        b'<link src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">'
        b'</head><body>Hello!</body></html>')


def test_injector_inline_renderer():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = components.includer(environ)
        include('jquery', bowerstatic.renderer.render_inline_js)
        return [b'<html><head></head><body>Hello!</body></html>']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (
        b'<html><head><script type="text/javascript">/* jquery.js 2.1.1 */\n'
        b'</script></head><body>Hello!</body></html>')


def test_injector_no_content_type_set():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [])
        include = components.includer(environ)
        include('jquery/dist/jquery.js')
        return [b'SOME-BINARY-OR-NOT-HTML-DATA']

    injector = bower.injector(wsgi)

    c = Client(injector)

    response = c.get('/')
    assert response.body == (b'SOME-BINARY-OR-NOT-HTML-DATA')
