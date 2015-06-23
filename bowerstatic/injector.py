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
        if response.content_type is None:  # e.g. 401 reponses
            return response
        if response.content_type.lower() not in CONTENT_TYPES:
            return response
        inclusions = request.environ.get('bowerstatic.inclusions')
        if inclusions is None:
            return response
        body = response.body
        response.body = b''
        rendered_inclusions = (inclusions.render() + '</head>').encode('utf-8')        
        body = body.replace(b'</head>', rendered_inclusions)
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
