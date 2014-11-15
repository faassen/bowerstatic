import webob
from webob.static import FileApp
import time


MINUTE_IN_SECONDS = 60
HOUR_IN_SECONDS = MINUTE_IN_SECONDS * 60
DAY_IN_SECONDS = HOUR_IN_SECONDS * 24
YEAR_IN_SECONDS = DAY_IN_SECONDS * 365

# arbitrarily define forever as 10 years in the future
FOREVER = YEAR_IN_SECONDS * 10


class PublisherTween(object):
    def __init__(self, bower, handler):
        self.bower = bower
        self.handler = handler

    def __call__(self, request):
        # first segment should be publisher signature
        publisher_signature = request.path_info_peek()
        # pass through to underlying WSGI app
        if publisher_signature != self.bower.publisher_signature:
            return self.handler(request)
        request.path_info_pop()
        # next segment is BowerComponents name
        bower_components_name = request.path_info_pop()
        if bower_components_name is None:
            return webob.exc.HTTPNotFound()
        # next segment is component name
        component_name = request.path_info_pop()
        if component_name is None:
            return webob.exc.HTTPNotFound()
        # next segment is component version
        component_version = request.path_info_pop()
        if component_version is None:
            return webob.exc.HTTPNotFound()
        # the rest of the path goes into component
        file_path = request.path_info.lstrip('/')
        if file_path.strip() == '':
            return webob.exc.HTTPNotFound()
        filename = self.bower.get_filename(bower_components_name,
                                           component_name,
                                           component_version,
                                           file_path)
        if filename is None:
            return webob.exc.HTTPNotFound()
        file_app = FileApp(filename)
        response = request.get_response(file_app)
        if response.status_code == 200:
            response.cache_control.max_age = FOREVER
            response.expires = time.time() + FOREVER
        # XXX do we really want to rely on mimetype guessing?
        return response


class Publisher(object):
    def __init__(self, bower, wsgi):
        def handler(request):
            return request.get_response(wsgi)
        self.tween = PublisherTween(bower, handler)

    @webob.dec.wsgify
    def __call__(self, request):
        return self.tween(request)
