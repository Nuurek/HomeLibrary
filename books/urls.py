from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r'^copy/create', BookCopyCreateView.as_view(), name='book_copy_create'),
    url(r'^create', BookCreateView.as_view(), name='book_create'),
    url(r'^preview', BookPreviewView.as_view(), name='book_preview'),
]