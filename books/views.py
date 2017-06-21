from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import ListView

from libraries.views import LibraryGuestTemplateView, LibraryGuestView
from .forms import BookForm, BookPreviewForm
from .models import BookCoverPreview, BookCopy, Book, GoogleBook
from .google_books_api import GoogleBooksAPI


class BookCopyCreateView(LibraryGuestView, ListView):
    template_name = 'books/book_copy_create.html'
    model = Book
    context_object_name = 'books'

    def get_queryset(self):
        return Book.objects.all()

    def get_context_data(self, **kwargs):
        context = super(BookCopyCreateView, self).get_context_data(**kwargs)
        context['library_pk'] = self.library.pk
        return context


class BookCreateView(LibraryGuestTemplateView, FormView):
    form_class = BookForm
    template_name = 'books/book_create.html'

    def get_initial(self):
        if 'book' in self.request.session:
            return self.request.session.pop('book')
        else:
            return None

    def form_valid(self, form):
        user_profile = self.request.user.userprofile
        try:
            BookCoverPreview.objects.get(profile=user_profile).delete()
        except BookCoverPreview.DoesNotExist:
            pass
        cover_preview = BookCoverPreview(profile=user_profile, cover=form.cleaned_data.pop('cover'))
        cover_preview.save()
        self.request.session['book'] = form.cleaned_data
        return super(BookCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('book_preview', kwargs={'library_pk': self.library.pk})


class BookPreviewView(LibraryGuestTemplateView):
    template_name = 'books/book_preview.html'

    def get_context_data(self, **kwargs):
        context = super(BookPreviewView, self).get_context_data(**kwargs)
        book_data = self.request.session['book']
        book = Book(book_data)
        book.cover = BookCoverPreview.objects.get(profile=self.request.user.userprofile).cover
        context['book'] = book
        return context

    def dispatch(self, request, *args, **kwargs):
        get_response = super().dispatch(request, *args, **kwargs)

        if request.method == 'POST':
            if 'book' in self.request.session:
                book_data = self.request.session.pop('book')
                cover_preview = get_object_or_404(BookCoverPreview, profile=request.user.userprofile)
                form = BookPreviewForm(book_data)
                if form.is_valid():
                    book = form.save()
                    book.cover = cover_preview.cover
                    book.save()
                    cover_preview.delete()
                    BookCopy.objects.create(library=self.library, book=book).save()
                else:
                    return HttpResponseForbidden()
                return HttpResponseRedirect(reverse_lazy('library_details', kwargs={'library_pk': self.library.pk}))
            else:
                return HttpResponseForbidden()
        else:
            return get_response


class GoogleBookView(LibraryGuestTemplateView):
    template_name = 'books/google_book.html'


class LibraryBookCopiesListView(LibraryGuestView, ListView):
    model = BookCopy
    template_name = 'books/book_copies_list.html'

    def get_queryset(self):
        query = self.request.GET['query']
        return BookCopy.objects.filter(
            library=self.library
        ).filter(
            Q(book__title__contains=query) | Q(book__author__contains=query)
        )


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/book_list.html'

    def get_queryset(self):
        query = self.request.GET['query']
        books = Book.objects.filter(Q(title__contains=query) | Q(author__contains=query))
        return books


class GoogleBookListView(LoginRequiredMixin, ListView):
    model = GoogleBook
    template_name = 'books/google_book_list.html'
    context_object_name = 'google_book_list'

    def get_queryset(self):
        query = self.request.GET['query']
        api = GoogleBooksAPI()
        books = api.search(query)
        return books
