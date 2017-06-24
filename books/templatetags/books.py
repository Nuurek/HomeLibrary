from django.template import Library

from books.models import BookCopy, Book

register = Library()


@register.inclusion_tag('books/tags/book_tag.html')
def render_book(book: Book):
    return {
        'title': book.title,
        'author': book.author,
        'description': book.description,
        'cover': book.cover.url if book.cover else None,
        'ebook_link': book.google_info.ebook_link if book.google_info else None,
        'pk': book.pk,
    }


@register.inclusion_tag('books/tags/google_book_tag.html')
def render_google_book(book: dict):
    return book
