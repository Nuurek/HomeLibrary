from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import BookCopy


class BookCopyCreateView(LoginRequiredMixin, CreateView):
    model = BookCopy
    fields = ('book', )
    template_name = 'books/create.html'
