import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.temp import NamedTemporaryFile
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import ListView

from libraries.models import BookCopy
from libraries.views import LibraryGuestTemplateView
from .forms import BookForm, BookPreviewForm
from .google_books_api import GoogleBooksAPI
from .models import BookCoverPreview, Book


class BookCreateFormView(LibraryGuestTemplateView, FormView):
    form_class = BookForm
    template_name = 'books/book_create.html'

    def get_initial(self):
        if 'book' in self.request.session:
            return self.request.session.pop('book')
        else:
            return None

    def form_valid(self, form):
        user_profile = self.request.user.userprofile
        if form.cleaned_data['cover'] is not None:
            try:
                BookCoverPreview.objects.get(profile=user_profile).delete()
            except BookCoverPreview.DoesNotExist:
                pass
            cover_preview = BookCoverPreview(profile=user_profile, cover=form.cleaned_data.pop('cover'))
            cover_preview.save()
        self.request.session['book'] = form.cleaned_data
        return super(BookCreateFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('book_preview', kwargs={'library_pk': self.library.pk})


class BookPreviewView(LibraryGuestTemplateView):
    template_name = 'books/book_preview.html'

    def get_context_data(self, **kwargs):
        context = super(BookPreviewView, self).get_context_data(**kwargs)
        try:
            book_data = self.request.session['book']
        except KeyError:
            raise Http404()
        book = Book(**book_data)
        book.cover = BookCoverPreview.objects.get(profile=self.request.user.userprofile).cover
        context['book'] = book
        return context

    def post(self, request):
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


class GoogleBookView(LibraryGuestTemplateView):
    template_name = 'books/google_book.html'

    def post(self, request):
        google_id = request.POST['google_id']
        api = GoogleBooksAPI()
        book_data: dict = api.get(google_id)

        cover = book_data.pop('cover')
        self.save_cover_preview(cover['url'], google_id)

        self.request.session['book'] = book_data
        return HttpResponseRedirect(reverse_lazy('book_preview', kwargs={'library_pk': self.library.pk}))

    def save_cover_preview(self, cover_url, google_id):
        user_profile = self.request.user.userprofile
        try:
            BookCoverPreview.objects.get(profile=user_profile).delete()
        except BookCoverPreview.DoesNotExist:
            pass

        image = self.download_cover(cover_url)
        cover_preview = BookCoverPreview(profile=user_profile)
        cover_preview.cover.save('google' + google_id, image, save=True)
        cover_preview.save()

    @staticmethod
    def download_cover(cover_url):
        response = requests.get(cover_url)
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(response.content)
        img_temp.flush()
        return img_temp


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/book_list.html'

    def get_queryset(self):
        query = self.request.GET['query']
        books = Book.objects.filter(Q(title__contains=query) | Q(author__contains=query))
        return books


class GoogleBookListView(LibraryGuestTemplateView):
    template_name = 'books/google_book_list.html'

    def get_context_data(self, **kwargs):
        context = super(GoogleBookListView, self).get_context_data(**kwargs)
        query = self.request.GET['query']
        api = GoogleBooksAPI()
        context['google_book_list'] = api.search(query)
        return context
