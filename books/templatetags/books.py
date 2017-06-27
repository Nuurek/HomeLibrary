from django.template import Library
from django.forms.models import model_to_dict

from books.models import Book
from libraries.models import BookCopy, Lending

register = Library()


@register.inclusion_tag('books/tags/book_tag.html')
def render_book(book: Book):
    return model_to_dict(book)


@register.inclusion_tag('books/tags/google_book_tag.html')
def render_google_book(book: dict):
    return book


@register.inclusion_tag('books/tags/book_copy_tag.html')
def render_book_copy(copy: BookCopy, **kwargs):
    context = book_copy_to_dict(copy)
    context['only_description'] = kwargs.get('only_description', False)
    context['is_owner'] = kwargs.get('is_owner', False)
    try:
        lending = copy.lending_set.get(is_completed=False)
        context['lending'] = lending

        library = kwargs.get('library')
        if library == lending.borrower:
            context['borrowed'] = True
            context['lender'] = copy.library.owner.user.username
        else:
            context['lent'] = True
            context['borrower'] = lending.borrower.owner.user.username if lending.borrower else None
    except Lending.DoesNotExist:
        pass
    return context


def book_copy_to_dict(copy: BookCopy):
    book_dict = model_to_dict(copy.book)
    book_dict.pop('id')
    copy_dict = model_to_dict(copy)
    copy_dict.update(book_dict)
    return copy_dict
