"""
In some instances you end up producing tons of views that actually do mostly
the same except for perhaps one or two lines. This module offers you a simple
alternative::

    from django_oopviews import create_view, BaseView

    class View1(BaseView):
        def __init__(self, request, *args, **kwargs):
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

In this example, the code in ``View1.__init__`` is shared between View1 and
View2, so you don't need to write it again.

If you want to share some HttpResponse post-processing, implement the
``BaseView.__after__(self, response_obj)`` method

For more details check out this `blog post`_

.. _blog post: http://zerokspot.com/weblog/1037/
"""

__all__ = ('create_view', 'View')


def create_view(klass):
    """
    This is the generator function for your view. Simply pass it the class
    of your view implementation (ideally a subclass of BaseView or at least
    duck-type-compatible) and it will give you a function that you can
    add to your urlconf.
    """
    view_instance = klass()
    def _func(*args, **kwargs):
        """
        Constructed function that actually executes your view instance.
        """
        before = getattr(view_instance, '__before__', None)
        after = getattr(view_instance, '__after__', None)
        if before is not None:
            args = list(args)
            response = before(args, kwargs)
            if response:
                return response
            args = tuple(args)
        response = view_instance(*args, **kwargs)
        if after is None:
            return response
        else:
            return after(response)
    setattr(_func, '_class', klass)
    return _func


class BaseView(object):
    """
    The Base-class for OOPViews. Inherit it and overwrite the __init__,
    __call__ and/or __after__ and __before__ methods.
    """

    def __call__(self, request, *args, **kwargs):
        """
        This is the method where you want to put the part of your code, that
        is absolutely view-specific.
        """
        raise RuntimeError, "You have to override BaseView's __call__ method"

View = BaseView
