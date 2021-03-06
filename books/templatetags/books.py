from django.template import Library
from django.forms.models import model_to_dict
from django.contrib.auth.models import User

from books.models import Book
from libraries.models import BookCopy, Lending, Reading

register = Library()


@register.inclusion_tag('books/tags/book_tag.html')
def render_book(book: Book):
    return model_to_dict(book)


@register.inclusion_tag('books/tags/google_book_tag.html')
def render_google_book(book: dict):
    return book


@register.inclusion_tag('books/tags/book_copy_tag.html')
def render_book_copy(copy: BookCopy, user: User, **kwargs):
    context = book_copy_to_dict(copy)
    clean = kwargs.get('clean', False)
    context['clean'] = clean
    if clean:
        context['only_description'] = True
    else:
        context['only_description'] = kwargs.get('only_description', False)
    library = kwargs.get('library')
    context['user_library'] = user.userprofile.home_library.pk
    context['is_owner'] = library == user.userprofile.home_library
    is_book_owner = copy.library == user.userprofile.home_library
    context['is_book_owner'] = is_book_owner
    context['is_read'] = Reading.objects.filter(copy=copy)
    is_kept_by_user = copy.is_kept_by(user.userprofile)
    context['is_kept_by_user'] = is_kept_by_user
    context['is_read'] = Reading.objects.filter(copy=copy, reader=user.userprofile, is_completed=False).exists()
    if is_kept_by_user:
        context['is_read'] = Reading.objects.filter(copy=copy, reader=user.userprofile, is_completed=False).exists()
    try:
        lending = copy.lending_set.get(is_completed=False)
        context['lending'] = lending

        library = kwargs.get('library')
        if library == lending.borrower:
            context['borrowed'] = True
            context['lender'] = copy.library.owner.user.username if copy.library else None
        else:
            context['lent'] = True
            context['borrower'] = lending.borrower.owner.user.username if lending.borrower else None

        context['is_return_available'] = is_book_owner or (lending.borrower and user == lending.borrower.owner.user)
    except Lending.DoesNotExist:
        context['is_lending_available'] = is_book_owner
    return context


def book_copy_to_dict(copy: BookCopy):
    book_dict = model_to_dict(copy.book)
    book_dict.pop('id')
    copy_dict = model_to_dict(copy)
    copy_dict.update(book_dict)
    return copy_dict
