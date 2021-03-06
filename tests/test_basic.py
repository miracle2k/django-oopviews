"""Test the basic functionality in a non-inheritance scenario.
"""

from django_oopviews import View, create_view


def test_init_called_on_creation():
    """Check that __init__ is only called when the view is constructed,
    not when it is actually executed.
    """
    class TestView(View):
        count = 0
        def __init__(self):
            self.count += 1
        def __call__(self, *args, **kwargs):
            return self.count
    testview = create_view(TestView)
    assert testview._instance.count == 1   # also tests access to ._instance
    assert testview() == 1


def test_before_is_called():
    """Test that the before-hook is called normally..
    """
    class TestView(View):
        def __before__(self, args, kwargs):
            self.dummy = 42
        def __call__(self, *args, **kwargs):
            return self.dummy
        def foo(self, *args, **kwargs):
            return self.dummy * 2
    testview = create_view(TestView)
    assert testview() == 42
    assert testview.foo() == 84


def test_before_can_modify_args():
    """Test that the before-hook can modify the call arguments.
    """
    class TestView(View):
        def __before__(self, args, kwargs):
            while args: args.pop(0)
            kwargs['newarg'] = 'foo'
        def __call__(self, *args, **kwargs):
            return len(args), len(kwargs)
    testview = create_view(TestView)
    assert testview() == (0,1)
    assert testview('a', 'b', bla='blub') == (0,2)


def test_before_can_return_response():
    """If the before-hook returns a value, the view-function
    is never called.
    """
    class TestView(View):
        def __before__(self, args, kwargs):
            return 99
        def __call__(self, *args, **kwargs):
            return 42
    testview = create_view(TestView)
    assert testview() == 99


def test_after_is_called():
    """Test that the after-hook is called normally.
    """
    class TestView(View):
        def __after__(self, response):
            return response * 2
        def __call__(self, *args, **kwargs):
            return 3
        def foo(self, *args, **kwargs):
            return 4
    testview = create_view(TestView)
    assert testview() == 6
    assert testview.foo() == 8


def test_proxy_what_attributes_are_wrapped():
    """Private and non-callable attributes of a view are not wrapped.
    """
    class TestView(View):
        foo = 1
        def _bar(self, *args, **kwargs):
            pass
    testview = create_view(TestView)
    assert not hasattr(testview, 'foo')
    assert not hasattr(testview, '_bar')