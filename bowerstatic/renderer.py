from .error import Error


class Renderer(object):
    def __init__(self):
        self._renderers = {}
        self.register('.js', render_js)
        self.register('.css', render_css)

    def register(self, ext, renderer):
        self._renderers[ext] = renderer

    def html(self, resource):
        url = resource.url()
        try:
            return self._renderers[resource.ext](url)
        except KeyError:
            raise Error("Unknown extension for url: %s" % url)


def render_js(url):
    return '<script type="text/javascript" src="%s"></script>' % url


def render_css(url):
    return '<link rel="stylesheet" type="text/css" href="%s" />' % url
