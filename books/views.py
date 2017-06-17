from django.views.generic import CreateView, FormView, TemplateView
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
    success_url = reverse_lazy('book_preview')

    def form_valid(self, form):
        user_profile = self.request.user.userprofile
        BookCoverPreview.objects.filter(profile=user_profile).delete()
        cover_preview = BookCoverPreview(profile=user_profile, cover=form.cleaned_data.pop('cover'))
        cover_preview.save()
        self.request.session['book'] = form.cleaned_data
        return super(BookCreateView, self).form_valid(form)


class BookPreviewView(LoginRequiredMixin, TemplateView):
    template_name = 'books/book_preview.html'

    def get_context_data(self, **kwargs):
        context = super(BookPreviewView, self).get_context_data(**kwargs)
        book = self.request.session['book']
        book['cover'] = BookCoverPreview.objects.get(profile=self.request.user.userprofile).cover.url
        context['form'] = BookForm(book)
        context['book'] = book
        return context
