BowerStatic
===========

Introduction
------------

BowerStatic is a WSGI component that can serve static resources from
front-end packages (JavaScript, CSS) that you install through the
Bower_ package manager.

.. _Bower: http://bower.io/

Features:

* A WSGI-based server for static resources in Bower packages.

* Easily mark directories as being managed by Bower from Python, so that
  static resources in them will be served.

* Automatically includes URLs to static resources in HTML pages when
  you want it from Python, using ``<script>`` and ``<link>`` tags.

* Support for infinite caching of URLs by the browser and/or HTTP
  caching servesr.

* Instantly bust the cache when a new version of Bower package is
  installed.

* Development mode for Bower packages, meaning it busts the cache as
  soon as you make changes to code.

* Serves static resources on URLs that can be cached infinitely by the

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   tutorial

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
