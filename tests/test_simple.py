"""Test the ``simple`` special view module.
"""

from nose.tools import assert_raises
from django_oopviews import simple, create_view


def test_args():
    class TestView(simple.SimpleView):
        args = ['id']
        def __call__(self, foo):
            return self.request, self.id, foo
    testview = create_view(TestView)
    assert testview('request', 1, 'bar') == ('request', 1, 'bar')


def test_kwargs():
    class TestView(simple.SimpleView):
        kwargs = {'search_order': 'ASC'}
        def __call__(self):
            return self.search_order
    testview = create_view(TestView)
    assert testview('request') == 'ASC'
    assert testview('request', search_order='DSC') == 'DSC'


def test_mixed():
    """Test positional arguments passed via keyword.
    """
    class TestView(simple.SimpleView):
        args = ['id']
        def __call__(self, foo):
            return self.request, self.id, foo
    testview = create_view(TestView)

    # generally is a possibility...
    assert testview('request', foo='bar', id=1) == ('request', 1, 'bar')
    # ...but only if the correct order is maintained: here 'id' would
    # have two values, 'bar' and 1.
    assert_raises(TypeError, testview, 'request', 'bar', id=1)