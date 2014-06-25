Tutorial
========

The Bower object
----------------

To get started with BowerStatic you need a ``Bower``
instance. Typically you only have one global ``Bower`` instance in
your application.

You create it like this::

  import bowerstatic

  bower = bowerstatic.Bower()

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

You can register multiple ``bower_components`` directories with the
``bower`` object. You need to give each a unique name; in the example
it is ``components``. This name is used in the URL used to serve
components in this directory to the web.

The object returned we assign to a variable ``components`` that we use
later.

Including Static Resources in a HTML page
-----------------------------------------

Now that we have a ``components`` object we can start including static
resources from these components in a HTML page. BowerStatic provides
an easy, automatic way for you to do this from Python.

Using the ``components`` object we created earlier for a
``bower_components`q directory, you create a ``include`` function::

  include = components.includer(environ)

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

  BowerStatic's includer system needs to interact with the WSGI
  ``environ`` object. To get to ``environ`` in your framework a good bet
  is to try ``request.environ``; this should work in most frameworks.

  Your web framework may also have special integration with
  BowerStatic; in that case the integration takes care of getting the
  ``environ`` for you.

  .. _WSGI: http://wsgi.readthedocs.org/en/latest/

You need to create the ``include`` function within your WSGI
application, typically just before you want to use it. You need to
pass in the WSGI ``environ`` object, as this is where the inclusions
are stored. You can create the ``include`` function as many times as
you like for a WSGI environ; the inclusions are shared.

Now that we have ``include``, we can use it to include resources::

  include('jquery/dist/jquery.js')

This specifies you want to include the ``dist/jquery.js`` resource
from within the installed ``jquery`` package. This refers to an actual
file in the jQuery component; in ``bower_components`` there is a
directory ``jquery`` with the sub-path ``dist/jquery.js`` inside. It
is an error to refer to a non-existent file.

If you call ``include`` somewhere in code where also a HTML page is
generated, BowerStatic adds the following ``<script>`` tag to that
HTML page automatically::

  <script
    type="text/javascript"
    src="/bowerstatic/components/jquery/2.1.1/dist/jquery.js">
  </script>

URL structure
-------------

Let's look at the URLs used by BowerStatic for a moment::

  /bowerstatic/components/jquery/2.1.1/dist/jquery.js

``bowerstatic``
  The BowerStatic signature. You can change the default signature used
  by passing a ``signature`` argument to the ``Bower`` constructor.

``components``
  The unique name of the bower directory which you gave when you did an ``.add``.

``jquery``
  The name of the installed package as given by the ``name``
  field in ``bower.json``.

``2.1.1``
  The version number of the installed package as given by the ``version``
  field in ``bower.json``.

``dist/jquery.js``
  A relative path to a file within the package.

Caching
-------

BowerStatic makes sure that resources are served with caching headers
set to cache them forever [#forever]_. This means the browser does not
request them from the server again after loading them once. If you
install a caching proxy like Varnish or Squid in front of your web
server, or use Apache ``mod_cache``, the WSGI server only has to serve
the resource once, and then it served by cache forever.

Caching forever would not normally be advisable as it would make it
hard to upgrade to newer versions of packages. You would have to teach
your users to issue a shift-reload to get the new version of
JavaScript code. But with BowerStatic this is safe, as it includes the
version number of the package in the URLs. When a new version of a
package is installed, the version number is updated, and new URLs are
generated by the include mechanism.

.. [#forever] Well, for 10 years. But that's forever in web time.

Main endpoint
-------------

Bower has a concept of a ``main`` end-point for a package in its
``bower.json``. You can include the main endpoint by including the
package without any specific file::

  include('jquery')

This includes the file listed in the ``main`` field in ``bower.json``.
In the case of jQuery, this is the same file as we already included
in the earlier examples: ``dist/jquery.js``.

A package can also specify an array of files in ``main``. In this case
the first endpoint listed in this array is included.

The endpoint system is aware of Bower intra-package dependencies.
Suppose you include 'jquery-ui'::

  include('jquery-ui')

The ``jquery-ui`` package specifies in the ``dependencies`` field in
its ``bower.json`` that it depends on the ``jquery`` package. When you
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


Publisher: Serving Static Resources
-----------------------------------

Now that the ``bower`` object knows about which Bower directories to
serve, you can let it serve its contents as static resources. You need
to use a special WSGI framework component to do this, the
publisher. You wrap your WSGI application with this framework
component to give it the ability to serve these static resources to
the web. Here's how you do this::

  app = bower.publisher(my_wsgi_app)

``app`` is now a WSGI application that does everything ``my_wsgi_app``
does, as well as serve Bower components under the special URL
``/bowerstatic``.

Injector: Injecting Static Resources
------------------------------------

BowerStatic also automates the inclusion of static resources in your
HTML page, by inserting the appropriate ``<script>`` and ``<link>``
tags. This is done by another WSGI framework component, the injector.

You need to wrap the injector around your WSGI application as well::

  app = bower.injector(my_wsgi_app)

Wrap: Doing it all at once
--------------------------

Typically you will need both the injector and the publisher to wrap
your WSGI application. You can do this by hand::

  app = bower.publisher(bower.injector(my_wsgi_app))

but you can also do it in one easy step::

  app = bower.wrap(my_wsgi_app)


Local components
----------------

Now we have a way to publish and use Bower packages. But you also
develop your own front-end code: we call these "local
components". BowerStatic also helps with that. For this it is
important to understand that locally developed code has special
caching requirements:

* When you release a local component, you want it to be cached
  infinitely just like for Bower components.

  When later a new release is made, you want that cache to be
  invalidated, and not force end-users to do a shift-reload to get
  their browser to load the new version of the code.

  We can accomplish this behavior by using a version number in the
  URL, just like for Bower components.

  XXX one way to release a local component would be to release it
  as a bower component at this point. But this may be cumbersome
  for code maintained as part of Python package.

* When you *develop* a local component, you want the cache to be
  invalidated as soon as you make any changes to the code, so you
  aren't forced to do shift-reload during development. A simple reload
  should refresh all static resources.

  A way to look at this is that you want the system to make a new
  version number for each and every edit to the local component.

To have local components, you first need a special local components
registry::

  local = bower.local_components('local', components)

The first argument is the name of the local components registry. It is
used in the URL. The second argument is a reference to a bower
components directory that you've created earlier with
``bower.components()``. The local components registry can depend on
the components installed with Bower.

You can have more than one local components registry, but typically
you only need one per project.

Note that the local components registry does not point to a
``bower_components`` directory in order to find its
components. Instead we register individual component directories
manually.

Here's how we add a local component::

  local.component('/path/to/directory/mycode')

The rest of the relevant information is in its
``bower.json``. BowerStatic uses ``name`` and ``main`` and
``dependencies`` just like for third party components you have
installed with Bower. For how the version number is extracted see
below.

The name of the component should be unique within the local registry,
as well as not conflict with any component in the Bower components
registry.

The directory with client-side code in it can have any structure. It
could have a ``bower.json`` in it, but this is not inspected by the
local components registry. You could organize it so that the local
component is within a Python package.

If you have a file ``app.js`` in the local component directory, it
is published under this URL::

  /bowerstatic/local/mycode/1.1.0/app.js

To be able to include it, we need to construct an includer that also
looks at the local components if it cannot find it in the
bower components::

  include = components.includer(environ, local=local)

You can now include ``app.js`` in ``mycode`` like this::

  include('mycode/app.js')

Versioning
~~~~~~~~~~

Let's consider versioning in more detail.

``version`` is the version number that the package should appear
under. You can pick this up from the application version, so that a
new release of the application automatically updates the version
number of all local packages (busting the cache).

You could for instance pick it up from the Python project's
``setup.py`` like this::

  import pkg_resources

  version = pkg_resources.get_distribution('myproject').version

You can also leave off ``version`` or set it to ``None``. This
triggers ``devmode`` for that local component. It causes the version
to be automatically determined from the code in the package, and be
different each time you edit the code. Since the version is included
in the URL to the package, this allows you to get the latest version
of the code as soon as you reload after editing a file. No
shift-reloads needed to reload the code!

Devmode is relatively expensive, as BowerStatic has to monitor the
local directory for any changes to update the version number. You
should make sure you don't able it during a release, but pass the real
version number itself.

If your application has a notion of a development mode that you can
somehow inspect during run-time, you can write a version function that
automatically returns ``None`` in development mode and otherwise returns
the application's version number. This ensures optimal caching behavior
during development and deployment both. Here's what this function could
look like::

  def get_version():
      if is_devmode_enabled():
          return None
      return pkg_resources.get_distribution('myproject').version

You can then use this function when you register a local component::

  local.component('mycode', '/path/to/directory/mycode', version=get_version())
