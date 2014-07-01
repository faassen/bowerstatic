History
=======

hurry.resource
--------------

In 2008 I (Martijn Faassen) built a library called
`hurry.resource`_. It could automatically insert the required
``<script>`` and ``<include>`` tags into HTML. You could describe
these resources in Python code. It was aware of resource dependencies,
and also had a facility to automatically included minified versions of
particular resources, or bundled versions that included a number of
files.

I used ``hurry.resource`` in the context of applications based on the
Grok_ framework. The Grok integration was involved; you had to hook in
at the right place to manipulate the HTML, and ``hurry.resource`` did
not serve static resources itself; it left that up to the web
framework too. While I had written ``hurry.resource`` to be
web-framework independent, to my knowledge nobody used it outside of
Grok/Zope 3.

``hurry.resource`` in turn was inspired by a library called
`zc.resourcelibrary`_, which did much the same but had a more limited
way to describe resources. The resource metadata system was inspired
by the system in `YUI 2`_.

.. _`hurry.resource`: https://pypi.python.org/pypi/hurry.resource/0.10

.. _`zc.resourcelibrary`: https://pypi.python.org/pypi/zc.resourcelibrary

.. _`YUI 2`: https://yui.github.io/yui2/

.. _grok: http://grok.zope.org

Fanstatic
---------

In 2010, I, Jan-Wijbrand Kolman and Jan-Jaap Driessen rewrote
``hurry.resource`` into a more capable library. We had the realization
that by going with WSGI and by making the system *serve* resources as
well, we could create a true web framework for static resources. We
decided to rebuild ``hurry.resource`` into Fanstatic_.

We were also inspired by the capabilities of `z3c.hashedresource`_, a
library for Zope 3 that could generate cache-busting URLs that aid
caching and development (see :ref:`caching`). Since Fanstatic controlled
both creating inclusions for resources as well as serving them, we
could bring cache busting behavior into Fanstatic.

Another clever hack of Fanstatic was to leverage the Python packaging
infrastructure (PyPI, setuptools, etc) to distribute static resources
and their descriptions. This way we could easily install a variety of
client-side libraries, as long as someone had wrapped them using
Fanstatic.  The community wrapped quite a few libraries.


Unlike ``hurry.resource``, Fanstatic is easy to integrate into any
WSGI-based web framework. This helped Fanstatic to become a moderately
successful open source project. It was adopted not only by Grok users,
but also by many others that use WSGI-based web frameworks. We got
quite a few contributions, and a range of advanced features were added
to Fanstatic beyond that ``hurry.resource`` already provided.

.. _`Fanstatic`: http://fanstatic.org

.. _`z3c.hashedresource`: https://pypi.python.org/pypi/z3c.hashedresource

BowerStatic
-----------

A bottleneck of Fanstatic is that someone needs to sit down and write
a Python package for each JavaScript project out there. This takes
time. To upgrade a package to a newer version can be cumbersome.
Fanstatic makes the developer of Python wrapper library the
intermediary, and while this intermediary can add value, they can also
be an obstacle.

By 2014, a lot had changed in the client-side world. Fanstatic's
reliance on the Python packaging infrastructure was turning from an
advantage into a drawback. Bower_ has become the de-facto way for many
client-side libraries to be distributed and installed. Faced with the
task to wrap a range of JavaScript libraries using Fanstatic and then
maintain those wrapping libraries, I decided to give Fanstatic a
rethink instead.

Using the Bower package manager, we can install client-side components
without having to go through an intermediary.

Fanstatic has another limitation: just like in Python, you can only
have one version of a library installed per project. I was facing a
use case where this was not desirable: a large platform with multiple
sub-projects that might want to use divergent versions of their
client-side components.

So I started thinking about what a static web framework might look
like that uses Bower as its underlying packaging system, while
retaining some important features of Fanstatic, like automating
insertion of link and script tags, static resource serving, and
caching.

BowerStatic was born.

.. _Bower: http://bower.io/

