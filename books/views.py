from django.views.generic import CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import BookCopy, Book, BookCoverPreview
from .forms import BookForm


class BookCopyCreateView(LoginRequiredMixin, CreateView):
    model = BookCopy
    fields = ('book', )
    template_name = 'books/book_copy_create.html'


class BookCreateView(LoginRequiredMixin, FormView):
    form_class = BookForm
    template_name = 'books/book_create.html'
    success_url = reverse_lazy('library_list')

    def form_valid(self, form):
        cover_preview = BookCoverPreview(profile=self.request.user.userprofile, cover=form.cleaned_data['cover'])
        cover_preview.save()
        return super(BookCreateView, self).form_valid(form)
