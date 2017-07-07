from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.views.generic import TemplateView, ListView, View
from django.views.generic.edit import BaseDeleteView, BaseUpdateView, BaseCreateView, BaseFormView
from django.views.generic.list import BaseListView

from accounts.models import UserProfile
from books.forms import BookCopyForm
from libraries.models import BookCopy
from .forms import SendInvitationForm
from .models import Library, Invitation, Lending, Reading


class LibraryGuestTemplateView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    pk_url_kwarg = 'library_pk'
    raise_exception = True
    library = None
    is_owner = False

    def dispatch(self, request, *args, **kwargs):
        library_pk = kwargs.pop('library_pk')
        self.library = get_object_or_404(Library, pk=library_pk)
        self.is_owner = self.library.owner.user == self.request.user
        return super(LibraryGuestTemplateView, self).dispatch(request, *args, **kwargs)

    def test_func(self):
        profile = self.request.user.userprofile
        return profile == self.library.owner or profile in self.library.users.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['library'] = self.library
        context['library_pk'] = self.library.pk
        context['is_owner'] = self.is_owner
        return context


class LibraryOwnerTemplateView(LibraryGuestTemplateView):

    def test_func(self):
        profile = self.request.user.userprofile
        return profile == self.library.owner


class LibraryDetailsView(LibraryGuestTemplateView):
    template_name = 'libraries/details.html'


class LibraryManagementView(BaseFormView, LibraryOwnerTemplateView):
    template_name = 'libraries/management.html'
    form_class = SendInvitationForm
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['library'] = self.library
        context['guests'] = self.library.users.all()
        context['invitations'] = Invitation.objects.filter(library=self.library)
        return context

    def form_valid(self, form):
        invitation = Invitation(library=self.library, email=form.cleaned_data['email'],
                                confirmation_code=get_random_string(32))
        invitation.save()
        domain = get_current_site(self.request)
        invitation.send_invitation_email(domain)

        messages.success(self.request, "Invitation for " + invitation.email + " sent")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('library_management', kwargs={'library_pk': self.library.pk})


class LibraryNameUpdateView(BaseUpdateView, LibraryOwnerTemplateView):
    template_name = 'libraries/update.html'
    model = Library
    fields = ('name', )

    def get_object(self, queryset=None):
        return self.request.user.userprofile.home_library

    def form_valid(self, form):
        library = self.request.user.userprofile.home_library
        library.is_name_default = False
        library.save()
        messages.success(self.request, "Library name changed to " + library.name)
        return super().form_valid(form)


class InvitationConfirmationView(TemplateView):
    template_name = 'libraries/invitation_confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        library_id = kwargs['library_pk']
        confirmation_code = kwargs['code']
        library = Library.objects.get(pk=library_id)
        user = self.request.user
        try:
            invitation = Invitation.objects.get(library=library, email=user.email, confirmation_code=confirmation_code)
            library.users.add(user.userprofile)
            invitation.delete()
            context['success'] = True
            context['library'] = library
        except (ObjectDoesNotExist, AttributeError):
            context['success'] = False

        return context


class InvitationDeleteView(BaseDeleteView, LibraryOwnerTemplateView):
    model = Invitation
    success_url = reverse_lazy('library_management')
    template_name = 'libraries/invitation_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, "Invitation for " + self.object.email + " deleted")
        return reverse_lazy('library_management', kwargs={'library_pk': self.library.pk})


class GuestDeleteView(BaseDeleteView, LibraryOwnerTemplateView):
    model = UserProfile
    template_name = 'libraries/guest_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        guest: UserProfile = self.get_object()
        Lending.objects.filter(borrower=guest.home_library).update(is_completed=True, return_date=timezone.now())
        library = self.request.user.userprofile.home_library
        library.users.remove(guest)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        messages.success(self.request, "Access for " + self.object.user.username + " has been revoked")
        return reverse_lazy('library_management', kwargs={'library_pk': self.library.pk})


class LibrariesListView(ListView):
    model = Library
    template_name = 'libraries/list.html'

    def get_queryset(self):
        profile = self.request.user.userprofile
        return profile.libraries.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_library'] = self.request.user.userprofile.home_library
        return context


class BookCopyCreateView(LibraryGuestTemplateView):
    template_name = 'libraries/book_copy_create.html'

    def get(self, request, *args, **kwargs):
        self.request.session['copy_after_book_creation'] = True
        return super(BookCopyCreateView, self).get(request, *args, **kwargs)

    def post(self, request):
        form = BookCopyForm({'book': request.POST['book'], 'library': self.library.pk})
        if form.is_valid():
            copy: BookCopy = form.save()
            messages.success(self.request, "\"" + copy.book.title + "\" has been added to your library")
            return HttpResponseRedirect(reverse_lazy('library_details', kwargs={'library_pk': self.library.pk}))
        else:
            return HttpResponseForbidden()


class BookCopiesListView(BaseListView, LibraryGuestTemplateView):
    model = BookCopy
    template_name = 'libraries/book_copies_list.html'
    context_object_name = 'book_copies'

    def get_queryset(self):
        query = self.request.GET['query']
        book_copies = BookCopy.objects.filter(
            Q(library=self.library) | Q(Q(lending__borrower=self.library) & Q(lending__is_completed=False))
        ).distinct().filter(
            Q(book__title__icontains=query) | Q(book__author__icontains=query)
        ).order_by(
            'book__title'
        )
        return book_copies


class BookCopyDeleteView(BaseDeleteView, LibraryOwnerTemplateView):
    model = BookCopy
    template_name = 'libraries/book_copy_delete.html'

    def get_success_url(self):
        if self.request.session.get('copy_after_book_creation', True):
            messages.success(self.request, "\"" + self.object.book.title + "\" has been deleted from your library")
        return reverse_lazy('library_details', kwargs={'library_pk': self.library.pk})


class BookCopyCommentUpdateView(BaseUpdateView, LibraryOwnerTemplateView):
    model = BookCopy
    fields = ('comment',)
    template_name = 'libraries/book_copy_comment.html'

    def get_success_url(self):
        messages.success(self.request, "Comment updated")
        return reverse_lazy('library_details', kwargs={'library_pk': self.library.pk})


class LendingCreateView(BaseCreateView, LibraryOwnerTemplateView):
    model = Lending
    fields = ('borrower',)
    template_name = 'libraries/lending_create.html'

    def test_func(self):
        if not super(LendingCreateView, self).test_func():
            return False

        book_copy = BookCopy.objects.get(pk=self.kwargs['pk'])

        if Lending.objects.filter(copy=book_copy, is_completed=False).exists():
            return False

        return True

    def get(self, request, *args, **kwargs):
        book_copy = get_object_or_404(BookCopy, pk=self.kwargs['pk'])
        if Reading.objects.filter(copy=book_copy, is_completed=False).exists():
            messages.info(self.request, "You can't lend a book that you're still reading")
            return HttpResponseRedirect(reverse_lazy('library_details', kwargs={'library_pk': self.library.pk}))
        return super(LendingCreateView, self).get(request, *args, **kwargs)
        
    def get_form(self, form_class=None):
        form = super(LendingCreateView, self).get_form(form_class)
        form.fields['borrower'].empty_label = "Outside the system"
        guests = self.library.users.all()
        form.fields['borrower'].queryset = Library.objects.filter(owner__in=guests)
        return form

    def get_context_data(self, **kwargs):
        context = super(LendingCreateView, self).get_context_data(**kwargs)
        context['book_copy'] = BookCopy.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        lending = form.save(commit=False)
        lending.copy = get_object_or_404(BookCopy, pk=self.kwargs['pk'])
        lending.save()
        messages.success(self.request, "\"" + lending.copy.book.title + "\" lent")
        return HttpResponseRedirect(reverse_lazy('library_details', kwargs={'library_pk': self.library.pk}))


class LendingDeleteView(BaseDeleteView, LibraryGuestTemplateView):
    model = Lending
    template_name = 'libraries/lending_delete.html'

    def get_object(self, queryset=None):
        return Lending.objects.get(copy=BookCopy.objects.get(pk=self.kwargs['pk']), is_completed=False)

    def get_context_data(self, **kwargs):
        context = super(LendingDeleteView, self).get_context_data(**kwargs)
        context['book_copy'] = BookCopy.objects.get(pk=self.kwargs['pk'])
        return context

    def delete(self, request, *args, **kwargs):
        lending = self.get_object()
        lending.is_completed = True
        lending.return_date = timezone.now()
        lending.save()

        try:
            reading = Reading.objects.get(copy=lending.copy, is_completed=False)
            reading.is_completed = True
            reading.save()
        except Reading.DoesNotExist:
            pass

        messages.success(self.request, "\"" + lending.copy.book.title + "\" returned")
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('library_details', kwargs={'library_pk': self.request.user.userprofile.home_library.pk})


class OutsideLendingCreateView(LibraryOwnerTemplateView):
    template_name = 'libraries/outside_lending_create.html'

    def get(self, request, *args, **kwargs):
        self.request.session['copy_after_book_creation'] = False
        return super(OutsideLendingCreateView, self).get(request, *args, **kwargs)

    def post(self, request):
        form = BookCopyForm({'book': request.POST['book'], 'library': None})
        if form.is_valid():
            book_copy = form.save()
            return HttpResponseRedirect(reverse_lazy('outside_lending_confirm', kwargs={
                'library_pk': self.library.pk,
                'pk': book_copy.pk,
            }))
        else:
            return HttpResponseForbidden()


class OutsideLendingConfirmView(LibraryOwnerTemplateView):
    template_name = 'libraries/outside_lending_confirm.html'

    def test_func(self):
        if not super(OutsideLendingConfirmView, self).test_func():
            return False

        book_copy = BookCopy.objects.get(pk=self.kwargs['pk'])
        if book_copy.library is not None:
            return False
        else:
            return True

    def get_context_data(self, **kwargs):
        context = super(OutsideLendingConfirmView, self).get_context_data(**kwargs)
        context['book_copy'] = BookCopy.objects.get(pk=self.kwargs['pk'])
        return context

    def post(self, request, *args, **kwargs):
        book_copy = BookCopy.objects.get(pk=kwargs.pop('pk'))
        lending = Lending.objects.create(copy=book_copy, borrower=self.library)
        lending.save()
        messages.success(self.request, "\"" + book_copy.book.title + "\" has been borrowed from outside")
        return HttpResponseRedirect(reverse_lazy('library_details', kwargs={'library_pk': self.library.pk}))


class BookCopyKeeperView(LoginRequiredMixin, UserPassesTestMixin, View):

    def __init__(self):
        self.book_copy = None
        self.reader = None
        super(BookCopyKeeperView, self).__init__()

    def test_func(self):
        self.reader = self.request.user.userprofile
        self.book_copy = BookCopy.objects.get(pk=self.kwargs['pk'])

        return self.book_copy.is_kept_by(self.reader)


class ReadingCreateView(BookCopyKeeperView):

    def post(self, request, pk):
        try:
            Reading.objects.get(copy=self.book_copy, is_completed=False)
            return HttpResponseForbidden()
        except Reading.DoesNotExist:
            reading = Reading.objects.create(copy=self.book_copy, reader=self.reader)
            reading.save()
            messages.success(self.request, "You have started reading \"" + self.book_copy.book.title + "\"")
            return HttpResponseRedirect(
                reverse_lazy('library_details', kwargs={'library_pk': self.reader.home_library.pk})
            )


class ReadingDeleteView(BookCopyKeeperView):

    def test_func(self):
        if not super(ReadingDeleteView, self).test_func():
            return False

        return Reading.objects.filter(copy=self.book_copy, is_completed=False).exists()

    def post(self, request, pk):
        try:
            reading = Reading.objects.get(copy=self.book_copy, reader=self.reader, is_completed=False)
            reading.end_date = timezone.now()
            reading.is_completed = True
            reading.save()
            messages.success(self.request, "You have ended reading \"" + self.book_copy.book.title + "\"")
            return HttpResponseRedirect(
                reverse_lazy('library_details', kwargs={'library_pk': self.reader.home_library.pk})
            )
        except Reading.DoesNotExist:
            return HttpResponseForbidden()
