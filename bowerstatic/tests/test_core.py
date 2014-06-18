import bowerstatic
from webtest import TestApp as Client
import os


def test_publisher():
    bower = bowerstatic.Bower()

    bower.add('bower_components', os.path.join(
        os.path.dirname(__file__), 'bower_components'))

    def wsgi(environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['Hello!']

    publisher = bower.publisher(wsgi)

    c = Client(publisher)

    # pass through to underlying WSGI app
    response = c.get('/')
    assert response.body == b'Hello!'

    # access bowerstatic bit

    response = c.get('/bowerstatic/bower_components/jquery/2.1.1/dist/jquery.js')
    assert response.body == b'/* jquery.js 2.1.1 */\n'


# def test_tracer_bullet():
#     bower = bowerstatic.Bower()
#     bower.add('bower_components', 'bower_components')
#     def wsgi(env, start_response):
#         pass
#     publisher = bower.publisher(wsgi)
#     injector = bower.injector(publisher)

#     includer = bower.includer('bower_components')
#     includer()


