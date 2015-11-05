import bowerstatic
from webtest import TestApp as Client
import os
import sys
import json
from datetime import datetime, timedelta
import pytest

from bowerstatic import compat
from bowerstatic import filesystem_microsecond_autoversion


def test_local_falls_back_to_components():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    local = bower.local_components('local', components)

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = local.includer(environ)
        include('jquery/dist/jquery.js')
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

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
        return [b'<html><head></head><body>Hello!</body></html>']

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


def test_local_external_dependencies():
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
        return [b'<html><head></head><body>Hello!</body></html>']

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

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = local.includer(environ)
        include('local_component')
        return [b'<html><head></head><body>Hello!</body></html>']

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


def test_local_with_missing_version():
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    local = bower.local_components('local', components)

    path = os.path.join(
        os.path.dirname(__file__), 'local_component_missing_version')

    with pytest.raises(ValueError) as err:
        local.component(path, version=None)
    assert str(err.value).startswith('Missing _release and version in')
    assert str(err.value).endswith('/tests/local_component_missing_version')


# FIXME: strictly speaking Linux ext3 also has a failing bug here,
# but I don't know how to reliably detect whether the filesystem has
# only second granularity so this will have to do
@pytest.mark.skipif(
    sys.platform == 'darwin',
    reason="Microsecond granularity does not work on Mac OS X")
def test_local_with_microsecond_auto_version(tmpdir):
    # need to cut things a bit of slack, as filesystem time can apparently
    # be ahead slightly
    after_dt = datetime.now() - timedelta(seconds=1)

    # create a bower component directory
    component_dir = tmpdir.mkdir('component')
    bower_json_file = component_dir.join('bower.json')
    bower_json_file.write(json.dumps({
        'name': 'component',
        'version': '2.1',  # should be ignored
        'main': 'main.js'
    }))
    main_js_file = component_dir.join('main.js')
    main_js_file.write('/* this is main.js */')

    # now expose it through local
    bower = bowerstatic.Bower(autoversion=filesystem_microsecond_autoversion)

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    local = bower.local_components('local', components)

    local.component(component_dir.strpath, version=None)

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = local.includer(environ)
        include('component/main.js')
        return [b'<html><head></head><body>Hello!</body></html>']

    wrapped = bower.wrap(wsgi)

    c = Client(wrapped)

    response = c.get('/')
    before_dt = datetime.now()

    def get_url_dt(response):
        s = compat.text_type(response.body, 'UTF-8')
        start = s.find('src="') + len('src="')
        end = s.find('"', start)
        url = s[start:end]
        parts = url.split('/')
        url_dt_str = parts[4]
        url_dt = datetime.strptime(url_dt_str, '%Y-%m-%dT%H:%M:%S.%f')
        return url_dt_str, url_dt

    url_dt_str, url_dt = get_url_dt(response)

    assert url_dt >= after_dt
    assert url_dt <= before_dt

    response = c.get('/bowerstatic/local/component/%s/main.js' % url_dt_str)
    assert response.body == b'/* this is main.js */'

    after_dt = datetime.now() - timedelta(seconds=1)

    # now we modify a file
    main_js_file.write('/* this is main.js, modified */')

    response = c.get('/')

    before_dt = datetime.now()

    original_url_dt_str, original_url_dt = url_dt_str, url_dt
    url_dt_str, url_dt = get_url_dt(response)
    assert original_url_dt_str != url_dt_str
    assert url_dt >= after_dt
    assert url_dt <= before_dt
    assert url_dt > original_url_dt

    c.get('/bowerstatic/local/component/%s/main.js' % original_url_dt_str,
          status=404)
    response = c.get('/bowerstatic/local/component/%s/main.js' %
                     url_dt_str)
    assert response.body == b'/* this is main.js, modified */'


def test_local_with_second_auto_version(tmpdir):
    # need to cut things a bit of slack, as filesystem time can apparently
    # be ahead slightly
    after_dt = datetime.now() - timedelta(seconds=1)

    # create a bower component directory
    component_dir = tmpdir.mkdir('component')
    bower_json_file = component_dir.join('bower.json')
    bower_json_file.write(json.dumps({
        'name': 'component',
        'version': '2.1',  # should be ignored
        'main': 'main.js'
    }))
    main_js_file = component_dir.join('main.js')
    main_js_file.write('/* this is main.js */')

    # now expose it through local
    # the default autoversioning scheme uses second granularity
    bower = bowerstatic.Bower()

    components = bower.components('components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    local = bower.local_components('local', components)

    local.component(component_dir.strpath, version=None)

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=UTF-8')])
        include = local.includer(environ)
        include('component/main.js')
        return [b'<html><head></head><body>Hello!</body></html>']

    wrapped = bower.wrap(wsgi)

    c = Client(wrapped)

    response = c.get('/')
    before_dt = datetime.now()

    def get_url_dt(response):
        s = compat.text_type(response.body, 'UTF-8')
        start = s.find('src="') + len('src="')
        end = s.find('"', start)
        url = s[start:end]
        parts = url.split('/')
        url_dt_str = parts[4]
        url_dt = datetime.strptime(url_dt_str, '%Y-%m-%dT%H:%M:%S')
        return url_dt_str, url_dt

    url_dt_str, url_dt = get_url_dt(response)

    assert url_dt >= after_dt
    assert url_dt <= before_dt

    response = c.get('/bowerstatic/local/component/%s/main.js' % url_dt_str)
    assert response.body == b'/* this is main.js */'

    after_dt = datetime.now() - timedelta(seconds=1)

    # now we modify a file
    main_js_file.write('/* this is main.js, modified */')

    response = c.get('/')

    before_dt = datetime.now()

    original_url_dt = url_dt
    url_dt_str, url_dt = get_url_dt(response)
    assert url_dt >= after_dt
    assert url_dt <= before_dt
    assert url_dt >= original_url_dt

    response = c.get('/bowerstatic/local/component/%s/main.js' %
                     url_dt_str)
    assert response.body == b'/* this is main.js, modified */'
