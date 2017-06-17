from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import BookCopy, Book


class BookCopyCreateView(LoginRequiredMixin, CreateView):
    model = BookCopy
    fields = ('book', )
    template_name = 'books/book_copy_create.html'


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    fields = ('title', 'description', 'page_count', 'author', 'cover')
    template_name = 'books/book_create.html'
    success_url = reverse_lazy('library_list')
