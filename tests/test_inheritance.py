"""Test various inheritance scenarios.
"""

from django_oopviews import View, create_view


class DummyBase(View):
    count = 0
    def __before__(self, args, kwargs):
        self.count += 1
    def __after__(self, response):
        return response * 2
    def foo(self, *args, **kwargs):
        return 21


def test_processing_hooks_are_inherited():
    """Processing hooks are inherited from base classes if missing.
    """
    class TestView(DummyBase):
        def __call__(self, *args, **kwargs):
            return self.count
    testview = create_view(TestView)
    assert [testview(), testview(), testview()] == [2, 4, 6]


def test_processing_hooks_can_be_overridden():
    """Base-class processing hooks can be overridden in child classes.

    Also tests that super() calls work.
    """
    class TestView(DummyBase):
        def __after__(self, response):
            return super(TestView, self).__after__(response) - 1
        def __call__(self, *args, **kwargs):
            return self.count
    testview = create_view(TestView)
    assert [testview(), testview(), testview()] == [1, 3, 5]


def test_view_functions_are_inherited():
    """A class shares all the view functions of it's bases.
    """
    class TestView(DummyBase):
        pass
    testview = create_view(TestView)
    assert testview.foo() == 42


def test_view_functions_can_be_overridden():
    """A class can override view functions of it's bases.

    Also tests that super() calls work.
    """
    class TestView(DummyBase):
        def foo(self, *args, **kwargs):
            return super(TestView, self).foo(*args, **kwargs) - 1
    testview = create_view(TestView)
    assert testview.foo() == 40


def test_nested_views():
    """Nested view classes work as expected.
    """
    class TestView(View):
        def __after__(self, response):
            return response * 2
        class sub(View):
            def __call__(self, *args, **kwargs):
                return 1
            def foo(self, *args, **kwargs):
                return 42
    testview = create_view(TestView)

    # the nested view is usable normally; processing hooks of
    # outer levels are not called (TODO: but should they be?)
    assert testview.sub() == 1
    assert testview.sub.foo() == 42