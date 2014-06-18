import bowerstatic

def test_tracer_bullet():
    bower = bowerstatic.Bower()
    bower.add('foo', 'foo_dir')
    bower.add('bar', 'bar_dir')
    def wsgi(env, start_response):
        pass
    publisher = bower.publisher(wsgi)
    injector = bower.injector(publisher)

    foo_includer = bower.includer('foo')
    foo_includer()
    foo_includer('file.js')

