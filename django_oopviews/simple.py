from base import View


class SimpleView(View):
    """Passes parameters that are shared by multiple views as class
    attributes, keeping method signatures simple.

    Example:

        class BookView(SimpleView):
            args = ['id']
            kwargs = {'limit': 30}

            def by_author(self):
                return something(self.request, self.id, self.limit)
            def by_publisher(self):
                # ...
            def by_most_read(self):
                # ...

        book = create_view(BookView)
        book.by_author(request, 10)
        book.by_publisher(request, 10, limit=100)

    Note that ``request`` is automatically shared and does not need
    to be specified in ``args``.

    TODO: could be extended to support args being passed as kwargs.
    """

    args = []
    kwargs = {}

    def __before__(self, args, kwargs):
        shared_args = ['request'] + getattr(self, 'args', [])
        shared_kwargs = getattr(self, 'kwargs', {})

        for name in shared_args:
            setattr(self, name, args.pop(0))
        for name, default in shared_kwargs.items():
            setattr(self, name, kwargs.pop(name, default))

