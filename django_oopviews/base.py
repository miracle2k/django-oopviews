"""
In some instances you end up producing tons of views that actually do mostly
the same except for perhaps one or two lines. This module offers you a simple
alternative::

    from django_oopviews import create_view, BaseView

    class View1(BaseView):
        def __before__(self, request, args, kwargs):
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

If you want to share some HttpResponse post-processing, implement the
``BaseView.__after__(self, response_obj)`` method

For more details check out this `blog post`_

.. _blog post: http://zerokspot.com/weblog/1037/
"""

__all__ = ('create_view', 'View')


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


class InvocationProxyBase(object):
    """Used as a base class for all the classes created by the
    ``InvocationProxyMaker`` metaclass.
    """

    def _call_view(self, func, args, kwargs):
        """Used by the proxy whenever it needs to execute a view.

        Makes sure the pre- and post-processing runs.
        """
        if self.__before__ is not None:
            args = list(args)
            response = self.__before__(args, kwargs)
            if response:
                return response
            args = tuple(args)
        response = func(*args, **kwargs)
        if self.__after__ is None:
            return response
        else:
            return self.__after__(response)


class InvocationProxyMaker(type):
    """Metaclass that will create a proxy-class for a ``BaseView``
    given by the user.

    The invocation proxy will make sure that when the view methods are
    invoked, they are wrapped inside our pre- and post-processing chain.

    Works recursively, so nested ``View`` classes work as expected.
    """

    def __new__(cls, name, bases, attrs):
        if not '__view__' in attrs:
            raise RuntimeError('the __view__ attribute is required')
        view_instance = attrs.pop('__view__')

        # transfer the special before, after methods
        attrs['__before__'] = getattr(view_instance, '__before__', None)
        attrs['__after__'] = getattr(view_instance, '__after__', None)

        # transfer wrapped versions of all non-private methods
        for attr_name in dir(view_instance):
            if attr_name.startswith('_') and not attr_name in ('__call__',):
                continue
            attr = getattr(view_instance, attr_name)

            if isinstance(attr, type) and issubclass(attr, BaseView):
                attrs[attr_name] = cls.make(attr)

            elif callable(attr):
                def make_wrapped(func):
                    def wrapped(self, *args, **kwargs):
                        # ``_call_view`` is expected to be defined by the bases
                        return self._call_view(func, args, kwargs)
                    return wrapped
                attrs[attr_name] = make_wrapped(attr)

        result = type(name, bases, attrs)
        setattr(result, '_instance', view_instance)
        return result

    @classmethod
    def make(cls, view_class, *args, **kwargs):
        """Generator function that creates an invocation proxy for your
        OOP view (a ``BaseView``-subclass).

        You can then use the proxy or it's methods inside your urlconf,
        and it will ensure that your view is pre- and post-processed
        correctly.

        Additional arguments given besides ``view_class`` will be passed
        on to the class constructor.

        .. note:: Why is the manual ``create_view`` call necessary.
           After all, a metaclass could be used to make each ``BaseView``
           subclass directly return a usuable proxy object.

           However, this makes subclassing views somewhat more akward,
           which now would have to work like this:

                class view1(View):
                    pass
                # view1 is a proxy

                class view2(view1.klass):
                    pass

           Subclassing ``view1`` directly would a) attempt to subclass
           a proxy instance, and b) even if that worked super() calls
           would go through pre-/post-processing for each inheritance
           level, which is not how it's supposed to work.
        """
        dispatcher = cls("%sProxy" % view_class.__name__,
                         (InvocationProxyBase,),
                         {'__view__': view_class(*args, **kwargs)})
        return dispatcher()

create_view = InvocationProxyMaker.make