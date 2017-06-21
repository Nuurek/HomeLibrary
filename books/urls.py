from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r'^copy/create$', BookCopyCreateView.as_view(), name='book_copy_create'),
    url(r'^create$', BookCreateView.as_view(), name='book_create'),
    url(r'^create/google$', GoogleBookView.as_view(), name='google_books'),
    url(r'^preview$', BookPreviewView.as_view(), name='book_preview'),
    url(r'^copy/list$', LibraryBookCopiesListView.as_view(), name='library_book_copies'),
    url(r'^copy/create/list$', BookListView.as_view(), name='books_list'),
    url(r'^create/google/list$', GoogleBookListView.as_view(), name='google_books_list'),
]