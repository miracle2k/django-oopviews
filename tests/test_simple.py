"""Test the ``simple`` special view module.
"""

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