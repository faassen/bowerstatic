import webob

CONTENT_TYPES = set(['text/html', 'application/xhtml+xml'])

METHODS = set(['GET', 'POST', 'HEAD'])


class Injector(object):
    def __init__(self, bower, wsgi):
        self.bower = bower
        self.wsgi = wsgi

    @webob.dec.wsgify
    def __call__(self, request):
        response = request.get_response(self.wsgi)
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
        body = body.replace(
            '</head>',
            '%s</head>' % inclusions.render())
        response.write(body)
        return response
