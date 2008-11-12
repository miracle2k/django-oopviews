###############
django-oopviews
###############

.. contents::

Base-implementation
===================

In some instances you end up producing tons of views that actually do mostly
the same except for perhaps one or two lines. This module offers you a simple
alternative::

    from django_oopviews import create_view, View

    class View1(View):
        def __before__(self, args, kwargs):
            # Here you have your common code
            self.my_variable = 1
        def __call__(self, request, *args, **kwargs):
            whatever = self.my_variable + 1
            return HttpResponse(whatever)

    class View2(View1):
        def __call__(self, request, *args, **kwargs):
            return HttpResponse(self.my_variable)

    view1 = create_view(View1)
    view2 = create_view(View2)

In this example, the code in ``View1.__before__`` is shared between View1 and
View2, so you don't need to write it again.

Note that you can modify ``args`` and ``kwargs`` within ``__before__``.

If you want to share some HttpResponse post-processing, implement the
``View.__after__(self, response_obj)`` method.

Your view classes may also contain any number of additional methods, which
then will be available as "views" in the same way the class itself is:

    class View1(View):
        def __call__(self, request):
            pass
        def foo(self, request):
            pass

    view1 = create_view(View1)
    view1()
    view1.foo()

Nested view objects are possible as well:

    class View1(View):
        class subview(View):
            def __call__(self, request):
                pass
    view1 = create_view(View1)
    view1.subview()

For more details check out this `blog post`_

.. _blog post: http://zerokspot.com/weblog/1037/

Addons
========

Content-Type-Negotitation with OOPViews
---------------------------------------

In some situations it comes in handy, to do some content type negotiation
to really provide an optimized view for the user depending on what a user's
application supports (say WML or HTML or XML over HTML). HTTP/1.1 handles
this using the "Accept"-request header to give the user the option, to say
what kind of content type she'd prefer or give a list of content types
prioritized with a value between 0 and 1.

This abstract view class should demonstrate, how you can easily handle such
situations within Django purely in the view code. The idea is pretty simple:
Simply use the ``__call__`` method as dispatcher for content-type-specific
methods.

To use this code, simply inherit the basic implementation and then specify
your content-type-specific methods and register them in the
``ctn_accept_binding``-dictionary::

    from django.http import HttpResponse
    from django_oopview import ctn

    class TestView(ctn.AbstractCTNView):
        ctn_accept_binding = {
            'text/html': 'html',
            'text/*': 'html',
            '*/*': 'html',
        }

        def html(self, request, *args, **kwargs):
            return HttpResponse("Hello", mimetype='text/html')

The ``ctn_accept_binding``-dictionary not only allows you to bind a method to a
content-type, but if you set a value to a tuple instead of just a string, it
will take the first element of that tuple as a priority value similar to the
one used in the "Accept"-handling. This way, you can prioritize methods for
the case, that the user requests any type of a given family like for instance
'text/\*'.

Simpler views using attributes for shared parameters
----------------------------------------------------

If you have a set of large views that share a common set of parameters they
receive (for example, all views in Django take the ``request``), the
``SimpleView`` extensions allows you to pass those arguments to your view
functions using attributes, rather than specifying them explicitly in every
signature:

    class BookView(SimpleView):
        args = ['id']
        kwargs = {'limit': 30}

        def by_author(self):
            print self.request, self.id, self.limit

        def by_publisher(self):
            # ...

        def by_most_read(self):
            # ...

    >>> book = create_view(BookView)
    >>> book.by_author(request, 10)
    <request object>, 10, 30
    >>> book.by_author(request, 15, limit=100)
    <request object>, 15, 100

Backwards-incompatible changes
==============================

Revision ?
    A view's ``__init__`` is now only called once, not everytime a view is
    called. Instead, do pre-processing in the new magic method ``__before__``.

    The hidden ``view._class`` attribute of the generated version of your
    view is gone. Instead, ``view._instance`` is available, and the class
    can still be accessed through ``view._instance.__class__``.

History
========

0.2 (Oct 1 2008)
    comes as its own library using setuptools and offering with the
    django_oopviews.ctn module a simple implementation of content negotiation
    in HTTP using OOPViews.

0.1 (inofficial)
    This version only included the BaseView as well as the create_view
    function and was bundled with the django-zsutils library.

