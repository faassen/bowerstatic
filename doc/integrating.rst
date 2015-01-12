Integrating BowerStatic
=======================

Introduction
------------

.. sidebar:: WSGI?

  WSGI_ is a Python standard for interoperability between web
  applications and web servers. It also allows you to plug in
  "middleware" that sit between web server and web application that
  adds extra functionality. BowerStatic provides such middleware,
  which we will see later.

  Most Python web frameworks are WSGI based. This means that if you
  use such a web framework for your application, your application is a
  WSGI application. Where this documentation says "WSGI application"
  you can read "your application".

  .. _WSGI: http://wsgi.readthedocs.org/en/latest/

This tutorial explains how to use BowerStatic with a WSGI
application. BowerStatic doesn't have a huge API, but your web
framework may provide more integration, in which case
you may only have to know even less.

The Bower object
----------------

To get started with BowerStatic you need a ``Bower``
instance. Typically you only have one global ``Bower`` instance in
your application.

You create it like this::

  import bowerstatic

  bower = bowerstatic.Bower()

Integrating BowerStatic with a WSGI app
---------------------------------------

For BowerStatic to function, we need to wrap your WSGI application
with BowerStatic's middleware. Here's to do this for our ``bower``
object::

  app = bower.wrap(my_wsgi_app)

Your web framework may have special BowerStatic integration instead
that does this for you.

Later on we will go into more details about what happens here (both an
injector and publisher get installed).

Declaring Bower Directories
---------------------------

Bower manages a directory in which it installs components (jQuery,
React, Ember, etc). This directory is called ``bower_components`` by
default. Bower installs components into this directory as
sub-directories. Bower makes sure that the components fit together
according to their dependency requirements.

Each ``bower_components`` directory is an "isolated universe" of
components. Components in a ``bower_components`` directory can depend
on each other only -- they cannot depend on components in another
``bower_components`` directory.

You need to let BowerStatic know where a ``bower_components``
directory is by registering it with the ``bower`` object::

  components = bower.components('components', '/path/to/bower_components')

Bowerstatic needs an absolute path to the components. With the help of
``module_relative_path`` you can use a path relative to the calling module::

  components = bower.components('components',
     bowerstatic.module_relative_path('path/relative/to/calling/module'))

You can register multiple ``bower_components`` directories with the
``bower`` object. You need to give each a unique name; in the example
it is ``components``. This name is used in the URL used to serve
components in this directory to the web.

The object returned we assign to a variable ``components`` that we use
later.

Including Static Resources in a HTML page
-----------------------------------------

.. sidebar:: Errors

  If you try to include a component that was not installed, you get an
  ``bowerstatic.Error`` exception. The ``bower_components`` directory
  is read during startup, so if you just installed that component
  using ``bower install``, you need to restart the server.

  If you try to refer to a refer to a file in a component that does
  not exist you also get an ``bowerstatic.Error`` exception. If that
  file then gets added (through a ``bower upgrade`` or if it's in a
  local component) it will be found without the need for a restart.

Now that we have a ``components`` object we can start including static
resources from these components in a HTML page. BowerStatic provides
an easy, automatic way for you to do this from Python.

Using the ``components`` object we created earlier for a
``bower_components`` directory, you create a ``include`` function::

  include = components.includer(environ)

You need to create the ``include`` function within your WSGI
application, typically just before you want to use it. You need to
pass in the WSGI ``environ`` object, as this is where the inclusions
are stored. You can create the ``include`` function as many times as
you like for a WSGI environ; the inclusions are shared.

Now that we have ``include``, we can use it to include resources::

  include('jquery/dist/jquery.js')

.. sidebar:: WSGI environ

  BowerStatic's includer system needs to interact with the WSGI
  ``environ`` object. If your WSGI-based web framework has a
  ``request`` object, then a very good bet is to try
  ``request.environ`` to get it.

  Your web framework may also have special integration with
  BowerStatic; in that case the integration can offer the ``include``
  function directly and takes care of interacting with the ``environ``
  for you.

This specifies you want to include the ``dist/jquery.js`` resource
from within the installed ``jquery`` component. This refers to an
actual file in the jQuery component; in ``bower_components`` there is
a directory ``jquery`` with the sub-path ``dist/jquery.js`` inside. It
is an error to refer to a non-existent file.

If you call ``include`` somewhere in code where also a HTML page is
generated, BowerStatic adds the following ``<script>`` tag to that
HTML page automatically::

  <script
    type="text/javascript"
    src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">
  </script>

Supporting additional types of resources
----------------------------------------

There are all kinds of resource types out there on the web, and
BowerStatic does not know how to include all of them on a HTML
page. Additional types can be added by making a renderer and
register that renderer to an extension.

Renderers will take a resource and returns a html snippet which will 
be injected in the HTML head element. Renderers can be defined as a
callable.

The callable will need to take the resource as the single argument.
Based on the resource, the callable can create a html snippet. The
following attributes of resource are useful for creating the html:

url
  The url which can be used to load the resource

content
  The content of the resource, which can used to make
  an inline resource. This is mainly useful for small
  resources as it reduces the numbers of http requests

An example::

  def render_foo(resource):
       return "<foo>%s</foo>" % resource.url

A renderer can be registered to resources types by::

  bower.renderer('.foo', render_foo)

If you now include a resource like ``example.foo``, that resource gets
included on the web page as ``<foo>/path/to/example.foo</foo>``.

Because most of the times, like above, the html can be constructed
with a format string, it is also possible to supply a string. Ie::

  bower.renderer('.foo', "<foo>{url}</foo>")

`url` and `content` are available in the string.

You can also use ``renderer()`` to override existing behavior of how a
resource with a particular extension is to be included.

If you include a resource with an unrecognized extension, a
``bowerstatic.Error`` is raised.


Custom renderer
---------------

It's also possible to specify the renderer which will be used in an
included resource, so the renderer of the resource type will be overriden
just for the given resource. When you specify the renderer, you can
again do that both as callable and format string::

   include('static/favicon.ico', '<link rel="shortcut icon" type="image/x-icon" href="{url}"/>')

or::

   include('static/favicon.ico', lambda resource: '<link rel="shortcut icon" type="image/x-icon" href="' + resource.url + '"/>')


URL structure
-------------

Let's look at the URLs used by BowerStatic::

  /bowerstatic/components/jquery/2.1.1/dist/jquery.js

``bowerstatic``
  The BowerStatic signature. You can change the default signature used
  by passing a ``signature`` argument to the ``Bower`` constructor.

``components``
  The unique name of the ``bower_components`` directory which you registered
  with the ``bower`` object.

``jquery``
  The name of the installed component as given by the ``name``
  field in ``bower.json``.

``2.1.1``
  The version number of the installed component as given by the ``version``
  field in ``bower.json``.

``dist/jquery.js``
  A relative path to a file within the component.

.. _caching:

Caching
-------

.. sidebar:: Cache busting

  Caches in the browser and caching servers such as Varnish like to
  hold on to static resources, so that the static resources does not
  to be reloaded all the time.

  But when you upgrade an application, or develop an application, you
  want the browser to request *new* resources from the server where
  those resources have changed.

  Cache busting is a simple technique to make this happen: you serve
  changed resources under a new URL. BowerStatic does this
  automatically for you by including a version number or timestamp in
  the resource URLs.

BowerStatic makes sure that resources are served with caching headers
set to cache them forever [#forever]_. This means that after the first
time a web browser accesses the browser, it does not have to request
them from the server again. This takes load off your web server.

To take more load off your web server, you can install a install a
caching proxy like Varnish or Squid in front of your web server, or
use Apache's ``mod_cache``. With those installed, the WSGI server only
has to serve the resource once, and then it is served by cache after
that.

Caching forever would not normally be advisable as it would make it
hard to upgrade to newer versions of components. You would have to
teach your users to issue a shift-reload to get the new version of
JavaScript code. But with BowerStatic this is safe, because it busts
the cache automatically for you. When a new version of a component is
installed, the version number is updated, and new URLs are generated
by the include mechanism.

.. [#forever] Well, for 10 years. But that's forever in web time.

Main endpoint
-------------

Bower has a concept of a ``main`` end-point for a component in its
``bower.json``. You can include the main endpoint by including the
component with its name without any file path after it::

  include('jquery')

This includes the file listed in the ``main`` field in ``bower.json``.
In the case of jQuery, this is the same file as we already included
in the earlier examples: ``dist/jquery.js``.

A component can also specify an array of files in ``main``. In this case
only the first endpoint listed in this array is included.

The endpoint system is aware of Bower component dependencies.
Suppose you include 'jquery-ui'::

  include('jquery-ui')

The ``jquery-ui`` component specifies in the ``dependencies`` field in
its ``bower.json`` that it depends on the ``jquery`` component. When you
include the ``jquery-ui`` endpoint, BowerStatic automatically also
include the ``jquery`` endpoint for you. You therefore get two
inclusions in your HTML::

  <script
    type="text/javascript"
    src="/bowerstatic/static/jquery/2.1.1/dist/jquery.js">
  </script>
  <script
    type="text/javascript"
    src="/bowerstatic/static/jquery-ui/1.10.4/ui/jquery-ui.js">
  </script>

If ``main`` lists a resource with an extension that has no renderer
registered for it, that resource is not included.

WSGI Publisher and Injector
---------------------------

Earlier we described ``bower.wrap`` to wrap your WSGI application with
the BowerStatic functionality. This is enough for many applications.
Sometimes you may want to be able to use the static resource
publishing and injecting-into-HTML behavior separately from each
other, however.

Publisher
~~~~~~~~~

BowerStatic uses the publisher WSGI middleware to wrap a WSGI
application so it can serve static resources automatically::

  app = bower.publisher(my_wsgi_app)

``app`` is now a WSGI application that does everything ``my_wsgi_app``
does, as well as serve Bower components under the special URL
``/bowerstatic``.

Injector
~~~~~~~~

BowerStatic also automates the inclusion of static resources in your
HTML page, by inserting the appropriate ``<script>`` and ``<link>``
tags. This is done by another WSGI middleware, the injector.

You need to wrap the injector around your WSGI application as well::

  app = bower.injector(my_wsgi_app)

Wrap
~~~~

Before we saw ``bower.wrap``. This wraps both a publisher and an injector
around a WSGI application. So this::

  app = bower.wrap(my_wsgi_app)

is equivalent to this::

  app = bower.publisher(bower.injector(my_wsgi_app))

Morepath integration
--------------------

See `static resources with Morepath`_ for information on how the
`more.static`_ extension helps you use BowerStatic in the `Morepath`_
web framework.

.. _`static resources with Morepath`: http://morepath.readthedocs.org/en/latest/more.static.html

.. _`more.static`: http://pypi.python.org/pypi/more.static

.. _Morepath: http://morepath.readthedocs.org

Pyramid integration
-------------------

For integration into the Pyramid_ web framework, there is a `pyramid_bowerstatic`_
extension or you can use `djed.static`_.

.. _`pyramid_bowerstatic`: https://pypi.python.org/pypi/pyramid_bowerstatic

.. _Pyramid: http://www.pylonsproject.org/

.. _`djed.static`: https://pypi.python.org/pypi/djed.static

Example Flask integration
-------------------------

The Flask_ web framework does not have a specific extension
integrating BowerStatic yet, but you can use BowerStatic's WSGI
integration layer to do so.  Here is an example of how you integrate
BowerStatic with Flask. This code assumes you have a
``bower_components`` directory next to this module::

    from flask import Flask, request
    import bowerstatic
    import os.path

    app = Flask(__name__)

    bower = bowerstatic.Bower()

    components = bower.components(
       'components',
        os.path.join(os.path.dirname(__file__), 'bower_components'))

    @app.route('/')
    def home():
        include = components.includer(request.environ)
        include('jquery')
        # it's important to have head and body elements in the
        # HTML so the includer has a point to include into
        return "<html><head></head><body></body></html>'

    if __name__ == "__main__":
        # wrap app.wsgi_wrap, not the Flask app.
        app.wsgi_app = bower.wrap(app.wsgi_app)
        app.run(debug=True)

In the example we used a simple text string but you can use Jinja
templates too. No special changes to the templates are necessary; the
only thing required is that they have HTML ``<head>``, ``</head>``,
``<body>`` and ``</body>`` tags so that the includer has a point where
it can include the static resources.

.. _Flask: http://flask.pocoo.org/

Using the Publisher and Injector with WebOb
-------------------------------------------

The ``Injector`` and ``Publisher`` can also directly be used with
WebOb_ request and response objects. This is useful for integration
with web frameworks that already use WebOb::

    from morepath import InjectorTween, PublisherTween

    def handle(request):
       ... do application's work, returning response ...

    # use wrapped_handle instead of handle to handle application
    # requests with BowerStatic support
    wrapped_handle = PublisherTween(bower, InjectorTween(bower, handle))

All that is required is a WebOb request and a response.

The Morepath and Pyramid integrations mentioned above already make use
of this API.

.. _WebOb: http://webob.org

