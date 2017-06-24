from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^form$', BookCreateFormView.as_view(), name='book_create'),
    url(r'^preview$', BookPreviewView.as_view(), name='book_preview'),
    url(r'^list$', BookListView.as_view(), name='books_list'),
    url(r'^google$', GoogleBookView.as_view(), name='google_books'),
    url(r'^google/list$', GoogleBookListView.as_view(), name='google_books_list'),
]