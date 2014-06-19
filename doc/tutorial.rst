Tutorial
========

Declaring Bower Components
--------------------------

You can declare directories as Bower components directories using
the following API::

  import bowerstatic

  bower = bowerstatic.Bower()

  bower.add('static', 'path/to/bower_components')

Serving Static Resources
------------------------

Serving static resources using BowerStatic involves a special
WSGI framework component, ``BowerPublisher``. If you want your
WSGI application to serve Bower components, you can wrap it in a
``BowerPublisher`` component::

  app = bower.publisher(my_wsgi_app)

``app`` is now a WSGI application that does everything ``my_wsgi_app``
does, as well as serve bower components under the special URL
``/bowerstatic``.

Including Static Resources in a HTML page
-----------------------------------------

Another WSGI framework component, ``BowerInjector``, can be used to
automatically include those static resources you want into a web page
using ``<script>`` and ``<link>`` tags and the like. First we wrap our
WSGI application in the ``BowerInjector``::

  app = bower.injector(my_wsgi_app)

``app`` now is a WSGI application that does everything ``my_wsgi_app``
does, as well as inject ``<script>`` and ``<link>`` tags when you
requested a static resource to be served.

We can create an includer from ``bower_directories`` for the ``static``
directory::

  static = bower.includer('static')

Here is how we refer to a static resource from Python (from somewhere
in code that results in HTML to be rendered)::

  static('jquery')

This includes the static resource indicated by ``main`` in the web
page. In case of jQuery this is ``dist/jquery.js``. This results in
the following ``<script>`` tag to be included in the HTML page::

  <script
    type="text/javascript"
    src="/bowerstatic/static/jquery/2.1.1/dist/jquery.js">
  </script>

You can also refer to other files that you know are in the installed
package::

  static('jquery', 'dist/jquery.min.js')

which results in this script tag::

  <script
    type="text/javascript"
    src="/bowerstatic/static/jquery/2.1.1/dist/jquery.min.js">
  </script>

Dependencies
------------

BowerStatic knows about dependencies set up between Bower directories
and can automate them. It will only do this when the ``main`` entry
point is automatically requested, not when you include individual files.

jQuery UI for instance depends on jQuery. So if you have ``jquery-ui``
installed, you can pull in its main file like this::

  static('jquery-ui')

Since its ``bower.json`` lists jquery as a dependency, it will also
include jQuery, resulting in two script tags::

  <script
    type="text/javascript"
    src="/bowerstatic/static/jquery/2.1.1/dist/jquery.js">
  </script>
  <script
    type="text/javascript"
    src="/bowerstatic/static/jquery-ui/1.10.4/ui/jquery-ui.js">
  </script>

More dependencies
-----------------

It can be useful to establish other dependencies between static
resources that you know about but that Bower doesn't list. There are a
range of ways to do this using JavaScript either, either on the
client-side (i.e. RequireJS) or on the server-side (i.e. Node-style
and browserify).

You can also supply additional dependency information
to ``BowerStatic`` if you so wish. We know for instance that a
minified version of jQuery UI is shipped in jquery-ui under the path
``ui/minified/jquery-ui.min.js``, and that a minified version of
jQuery is available under the path ``dist/jquery.min.js``. We
can establish this dependency as follows::

  bower.depends('static',
                resource=('jquery-ui', 'ui/minified/jquery-ui.min.js'),
                depends=[('jquery', 'dist/jquery.min.js')])

A resource is a tuple given the package name and a path within that
package to the resource. Here we specify that the ``jquery-ui.min.js``
resource depends on the ``jquery.min.js`` resource. Depends is a list,
as a resource may depend on multiple resources.

Now when you depend on ``jquery-ui.min.js`` you will also automatically
get the ``jquery.min.js`` resource::

  <script
    type="text/javascript"
    src="/bowerstatic/static/jquery/2.1.1/dist/jquery.min.js">
  </script>
  <script
    type="text/javascript"
    src="/bowerstatic/static/jquery-ui/1.10.4/ui/minified/jquery-ui.min.js">
  </script>

Thoughts
--------

* The 'bower' object may be a global, as in many setups you'd have
  only one. I chose to make it explicit though.

* You can change which ``bower_components`` directory is used by using
  a different includer, as bower components directories are mapped to
  names (in this case 'static').

* OO modeling. We could create a ``BowerComponents``, ``Package`` and
  ``Resource`` abstraction along the lines of Fanstatic, meaning it
  can be more than just a string or a tuple. This might make for a
  nice API. But it also might create dependencies between packages
  resources and the ``bower`` object, something Fanstatic has, but
  perhaps it'd be simpler to avoid it. I'll explore this during coding
  and writing tests.

* There is no notion of a Python package that contains dependency
  information, though those could be created; they could contain a
  function that takes a 'bower' object and then calls ``depends`` on
  it for whatever resource information they like.

* The system to mark dependencies could be expanded to mark other
  relationships between resources, including source versus minified
  version, or bundle versus individual bit. It might also be possible
  to export the dependency information to a client-side resource
  inclusion system like RequireJS.
