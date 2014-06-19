BowerStatic
===========

Introduction
------------

BowerStatic is a WSGI component that can serve static resources from
front-end packages (JavaScript, CSS) that you install through the
Bower_ package manager.

.. _Bower: http://bower.io/

Features:

* Integrates with any WSGI-based project.

* Easily serve Bower-managed directories.

* Easily say in Python code you want to include a static resource,
  which are then automatically inserted in any HTML page you
  generated. It uses the appropriate ``<script>`` and ``<link>`` tags.

* Support for Bower ``main`` end points. End points for dependencies
  are automatically included too.

* Declare additional dependencies from one resource to others, either
  in the same package or in others.

* Infinite caching of URLs by the browser and/or HTTP caching server for
  increased performance.

* Instantly bust the cache when a new version of Bower package is
  installed, avoiding force reload.

* Local packages with automatic cache busting as soon as you edit
  code.

Contents
--------

.. toctree::
   :maxdepth: 2

   tutorial
   dependencies

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
