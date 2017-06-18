from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView

from libraries.models import Library
from libraries.views import LibraryGuestMixin
from .forms import BookForm, BookPreviewForm
from .models import BookCoverPreview, BookCopy


class BookCopyCreateView(LibraryGuestMixin):
    template_name = 'books/book_copy_create.html'


class BookCreateView(LibraryGuestMixin, FormView):
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


class BookPreviewView(LibraryGuestMixin):
    template_name = 'books/book_preview.html'

    def get_context_data(self, **kwargs):
        context = super(BookPreviewView, self).get_context_data(**kwargs)
        book_data = self.request.session['book']
        book_data['cover'] = BookCoverPreview.objects.get(profile=self.request.user.userprofile).cover.url
        context['form'] = BookForm(book_data)
        context['book'] = book_data
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
