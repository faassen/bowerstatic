Dependencies
============

A Bower package may specify in its ``bower.json`` a dependency on
other packages. Bower uses this to install the dependent packags
automatically. The ``jquery-ui`` package for instance depends on the
``jquery`` package, so when you install ``jquery-ui``, the ``jquery``
package is automatically installed as well.

This is different from dependencies between individual static
resources. Bower has no information about these.

JavaScript has no standard ``import`` statement like Python
does. Instead, there are a many different ways to declare dependencies
between JavaScript modules, each with their own advantages and
drawbacks. One way to declare dependencies for client-side code is to
use ``RequireJS``. NodeJS has its way to declare dependencies between
modules on the server side, and tools like browserify can help to
bring these to the client. EcmaScript 6 is introducing a module syntax
of its own which will hopefully bring order to this chaos.

The strategy used to deliver a set of modules with dependencies to the
client is different than Python's: it's more like the way ``.so`` or
``.dll`` library files are built. Instead of shipping a package with a
lot of individual files, a single bundle is built from all the modules
in a package. ``dist/jquery.js`` for instance is a bundled version of
individual underlying jQuery modules that are developed in its ``src``
directory. This is done not only because JavaScript does not have a
native module system, but also because it's more efficient for a
browser to load a single bundle than many individual files.

A bundling module system like this has a drawback: you cannot declare
a dependency between modules in different Bower packages.

These module systems have a drawback: you cannot declare a dependency
between a module in one package and a module in another.

BowerStatic does not mandate a particular module system. Use whatever
system you like. BowerStatic does let you define dependency
relationships between JavaScript resources.

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
