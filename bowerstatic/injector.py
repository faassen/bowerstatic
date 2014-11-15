import webob

CONTENT_TYPES = set(['text/html', 'application/xhtml+xml'])

METHODS = set(['GET', 'POST', 'HEAD'])


class InjectorTween(object):
    def __init__(self, bower, handler):
        self.bower = bower
        self.handler = handler

    def __call__(self, request):
        response = self.handler(request)
        if request.method not in METHODS:
            return response
        if response.content_type.lower() not in CONTENT_TYPES:
            return response
        inclusions = request.environ.get('bowerstatic.inclusions')
        if inclusions is None:
            return response
        body = response.body
        response.body = b''
        body = body.replace(
            b'</head>', b''.join((inclusions.render().encode(), b'</head>')))
        response.write(body)
        return response


class Injector(object):
    def __init__(self, bower, wsgi):
        def handler(request):
            return request.get_response(wsgi)
        self.tween = InjectorTween(bower, handler)

    @webob.dec.wsgify
    def __call__(self, request):
        return self.tween(request)
