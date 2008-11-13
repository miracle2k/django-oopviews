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
    """

    args = []
    kwargs = {}

    def __before__(self, args, kwargs):
        shared_args = ['request'] + getattr(self, 'args', [])
        shared_kwargs = getattr(self, 'kwargs', {})

        for name in shared_args:
            # positional args may be passed as keywords, but only allow
            # that if all required positional arguments are filled, i.e.
            # it is not possible to pass a positional argument out of
            # order (the "got multiple values for keyword argument" error
            # in normal Python).
            if not args and name in kwargs:
                setattr(self, name, kwargs.pop(name))
            else:
                setattr(self, name, args.pop(0))
        for name, default in shared_kwargs.items():
            setattr(self, name, kwargs.pop(name, default))