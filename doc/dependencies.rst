Dependencies
============

Introduction
------------

.. sidebar:: Client-side JavaScript's "Shared Library" Approach

  JavaScript has no standard ``import`` statement like Python
  does. Instead, there are a many different ways to declare
  dependencies between JavaScript modules, each with their own
  advantages and drawbacks. One way to declare dependencies for
  client-side code is to use ``RequireJS``. NodeJS has its way to
  declare dependencies between modules on the server side, and tools
  like browserify exist that can help to bring these to the
  client. EcmaScript 6 is introducing a module syntax of its own which
  will hopefully bring order to this chaos.

  The JavaScript strategy commonly used to deliver a set of modules
  with dependencies to the client, especially for production use, is
  different than Python's: it's more like the way shared libraries
  work. A shared library (``.so`` on Unix systems, ``.dll`` on
  Windows) is built from many individual source files.

  So, instead of shipping a package with a lot of individual ``.js``
  files, a single bundle is built from all the modules in a
  package. ``dist/jquery.js`` for instance is a bundled version of
  individual underlying jQuery modules that are developed in its
  ``src`` directory.

  Bundling is done because client-side JavaScript does not have a
  universal module system, and also because it's more efficient for a
  browser to load a single bundle than to load many individual files.

  A bundling module system like this has a drawback: you cannot
  declare dependencies to individual modules in other
  packages. Instead such dependencies are on the package level.

A Bower package may specify in its ``bower.json`` a dependency on
other packages. Bower uses this to install the dependent packages
automatically. The ``jquery-ui`` package for instance depends on the
``jquery`` package, so when you install ``jquery-ui``, the ``jquery``
package is automatically installed as well.

BowerStatic also uses this information. If you include the endpoint of
a package (by not specifying the file), the endpoints of the
dependencies are also included automatically.

This is different from dependencies between individual static
resources. Bower has no information about these, and in fact there is
no universal system on the client to determine these.

Like Bower, BowerStatic therefore does not mandate a particular module
system. Use whatever system you like, with whatever server-side
bundling tools you like. But to help automate some cases, BowerStatic
does let you declare dependencies between resources if you want to,
either for resources within a single package or between resources in
different packages. This works for static resources of any kind;
JavaScript but also CSS.

Dependencies
-------------

In order to use dependencies you need to specify extra information for
resources. This is done using the resource method on the directory
object::

  components = bower.components('components', '/path/to/bower_components')

  components.resource(
     'jquery-ui/ui/minified/jquery-ui.min.js',
     dependencies=['jquery/dist/jquery.min.js'])

Here we express that the ``jquery-ui.min.js`` resource depends on the
``jquery.min.js`` resource.

When you now depend on ``jquery-ui/ui/minified/jquery-ui.min.js`` using
the same ``components`` object::

  include = components.includer(environ)
  include('jquery-ui/ui/minified/jquery-ui.min.js')

an inclusion to the minified jQuery is also generated::

  <script
    type="text/javascript"
    src="/bowerstatic/static/jquery/2.1.1/dist/jquery.min.js">
  </script>
  <script
    type="text/javascript"
    src="/bowerstatic/static/jquery-ui/1.10.4/ui/minified/jquery-ui.min.js">
  </script>

Resource objects
----------------

The ``.resource`` method in fact creates a resource object that
you can assign to a variable::

  jquery_min = components.resource(
     'jquery/dist/jquery.min.js')

You can use this resource object in an ``include``::

  include(jquery_min)

This has the same effect as referring to the resource directory using
a string.

You can also refer to this resource in another resource definition::

  jquery_ui_min = components.resource(
     'jquery-ui/ui/minified/jquery-ui.min.js',
     dependencies=[jquery_min])

Dealing with explicit resource objects can be handy as it saves
typing, and Python gives you an error if you refer to a resource
object that does not exist, so you can catch typos early.

Component objects
-----------------

It is sometimes useful to be able to generate the URL for a component
itself, for instance when client-side code needs to construct URLs to
things inside it, such as templates. To support this case,
you can get the URL of a component by writing this::

  components.get_component('jquery').url()

This will generate the appropriate versioned URL to that component.
