import os
from .error import Error


class Renderer(object):
    def __init__(self):
        self._renderers = {}
        self.register('.js', render_js)
        self.register('.css', render_css)
        self.register('.ico', render_favicon)
        self.register('.gif', render_favicon)
        self.register('.png', render_favicon)
        self.register('.jpg', render_favicon)

    def register(self, ext, renderer):
        self._renderers[ext] = make_renderer(renderer)

    def filter_by_known_ext(self, paths):
        result = []
        for path in paths:
            _, ext = os.path.splitext(path)
            if ext not in self._renderers:
                continue
            result.append(path)
        return result

    def renderer(self, resource):
        try:
            return self._renderers[resource.ext]
        except KeyError:
            raise Error("Unknown extension for url: %s" % resource.url())


def make_renderer(renderer):
    if isinstance(renderer, basestring):
        def string_renderer(resource):
            return renderer.format(url=resource.url(),
                                   content=resource.content())
        return string_renderer

    if callable(renderer):
        return renderer

    raise ValueError('Unknown renderer %s' % renderer)


render_js = '<script type="text/javascript" src="{url}"></script>'

render_inline_js = '<script type="text/javascript">{content}</script>'

render_css = '<link rel="stylesheet" type="text/css" href="{url}">'

render_inline_css = '<style>{content}</style>'

render_favicon = '<link rel="shortcut icon" href="{url}">'
