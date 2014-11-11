Local Components
================

Introduction
------------

Now we have a way to publish and use Bower components. But you
probably also develop your own front-end code: we call these "local
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

Usage
-----

To have local components, you first have to create a special local
components registry::

  local = bower.local_components('local', components)

You can have more than one local components registry, but typically
you only need one per project.

The first argument is the name of the local components registry. It is
used in the URL.

The second argument is a components object for a ``bower_components``
directory, created earlier with ``bower.components()``. This makes all
those bower components available in the local component registry, so
that the local components can depend on them.

Note that the local components registry does not point to a
``bower_components`` directory itself. Instead we register directories
for individual local components manually.

.. sidebar:: Location of the local component

  You can organize your code so that the local component lives inside
  a Python package that provides a web API for it to use, so that they
  can be developed together. You can also organize things differently
  -- this is up to you.

Here's how we add a local component::

  local.component('/path/to/directory/mycode', version='1.1.0')

The ``/path/to/directory/mycode`` directory should have a
``bower.json`` file. BowerStatic uses ``name`` and ``main`` for local
components like it uses them for third party Bower components. The
name of the component should be unique within the local registry, as
well as not conflict with any component in the Bower components
registry.

Bowerstatic needs an absolute path to the local components. With the help of
a utility function, you can use a path relative to the calling module::

  import bowerstatic.utility
  components = local.component(
      bowerstatic.utility.module_relative_path('path/relative/to/calling/module'),
      version='1.1.0')

``dependencies`` is also picked up from ``bower.json``, but unlike for
third party components these dependencies are not automatically
installed.

The version number is not picked up from ``bower.json``. Instead it is
passed through to the local component. This will make it possible to
support the right caching behavior. We go into detail about this
later.

If you have a local component called ``mycode``, and there is a file
``app.js`` in its directory, it is published under this URL::

  /bowerstatic/local/mycode/1.1.0/app.js

To be able to include it, we can create an includer for the ``local``
registry::

  include = local.includer(environ)

This includer can be used to include local components, but also the
third-party components from the registry that the local components
registry was initialized with.

You can now include ``app.js`` in ``mycode`` like this::

  include('mycode/app.js')

Versioning
----------

Let's consider versioning in more detail.

The version number is passed in when registering the local component.
We want it to do the right thing with caching:

* When the application is deployed, we want the version number to be
  the version number of that application (or sub-package of that
  application), so that infinite caching can be used but the cache is
  automatically busted with an application upgrade.

* When the application is under development, we want the version
  number to change each time you edit the local component's code, so that
  the cache is busted each time.

Versioning deployed applications
--------------------------------

You can use the version of a Python application easily, as long as it
is packaged using ``setuptools`` ( ``pip``, ``easy_install``,
``buildout``, etc). You can retrieve its version number like this::

  import pkg_resources

  version = pkg_resources.get_distribution('myproject').version

This picks up the version given in ``setup.py`` of ``myproject``.

Using this to obtain the version and passing it into
``local.component()`` is enough to make sure the cache is busted when
you make a release of your application.

Versioning during development
-----------------------------

We have to make sure the cache is busted automatically during
development as well. For that we have to turn on BowerStatic's
development mode. You can do this by passing ``None`` as the version
into ``local.component``.

This causes the version to be automatically determined from the code
in the package, and be different each time you edit the code. Since
the version is included in the URL to the package, this allows you to
get the latest version of the code as soon as you reload after editing
a file. No shift-reloads needed to reload the code!

Putting it all together
-----------------------

Development mode is relatively expensive, as BowerStatic has to
monitor the local directory for any changes so it can update the
version number automatically. You should therefore make sure it is
only enabled during development, not during deployment. When your
application is deployed you need to pass in a real version number, for
instance the one you pick up using ``pkg_resources`` as described
before.

If your application has a notion of a development mode that you can
somehow inspect during run-time, you can write a version function that
automatically returns ``None`` in development mode and otherwise
returns the application's version number. This ensures optimal caching
behavior during development and deployment both. Here's what this
function could look like::

  def get_version():
      if is_devmode_enabled():  # app specific API
          return None
      return pkg_resources.get_distribution('myproject').version

You can then register the local component like this::

  local.component('/path/to/directory/mycode', version=get_version())
