from django.shortcuts import render_to_response
from django.template import RequestContext
from base import View, create_view


__all__ = ('SimpleView', 'create_view',)


class SimpleView(View):
    """Passes parameters that are shared by multiple views as class
    attributes, keeping method signatures simple.

    Example:

        class BookView(SimpleView):
            args = ['id']
            kwargs = {'limit': 30}

            def __call__(self):
                return something(self.request, self.id, self.limit)
            def by_author(self):
                # ...
            def by_publisher(self):
                # ...
            def by_most_read(self):
                # ...

        book = create_view(BookView)
        book(request, 10)
        book.by_author(request, 10)
        book.by_publisher(request, 10, limit=100)

    Note that ``request`` is automatically shared and does not need
    to be specified in ``args``.

    There is a mechanism to share context values between the different
    subviews:

        class BookView(SimpleView):
            args = ['id']

            def _init_context():
                self.book = get_object_or_404(Book, pk=self.id)
                return {'book': self.book}

            def __call__():
                something_with(self.book)
                ...
                return 'template.html', {'foo': bar}

    The context returned by ``__call__`` will be merged with the base
    context returned by ``_init_context``, and used to render the
    template.
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
            setattr(self, name,
                # allow passing keywords as positional args
                kwargs.pop(name, args.pop() if args else default))

        prepared = self._init_context()
        if isinstance(prepared, dict):
            self._base_context = prepared
        else:
            return prepared  # can be used to return a result from here

    def __after__(self, response):
        if not isinstance(response, tuple):
            return response
        template_name, context = response
        self._base_context.update(context)
        return self._render(template_name, self._base_context)

    def _init_context(self):
        return {}

    def _render(self, template_name, context):
        return render_to_response(template_name, context,
            context_instance=RequestContext(self.request))