from django.template import Library
from django.forms.models import model_to_dict

from books.models import BookCopy, Book

register = Library()


@register.inclusion_tag('books/tags/book_tag.html')
def render_book(book: Book):
    return model_to_dict(book)


@register.inclusion_tag('books/tags/google_book_tag.html')
def render_google_book(book: dict):
    return book


@register.inclusion_tag('books/tags/book_copy_tag.html')
def render_book_copy(copy: BookCopy):
    book_dict = model_to_dict(copy.book)
    copy_dict = model_to_dict(copy)
    copy_dict.update(book_dict)
    return copy_dict
