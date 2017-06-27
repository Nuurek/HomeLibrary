from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import TemplateView, DeleteView, ListView
from django.views.generic.edit import BaseDeleteView, BaseUpdateView, BaseCreateView, BaseFormView
from django.views.generic.list import BaseListView
from datetime import datetime

from accounts.models import UserProfile
from books.forms import BookCopyForm
from libraries.models import BookCopy
from .forms import SendInvitationForm
from .models import Library, Invitation, Lending


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
        return reverse_lazy('library_management', kwargs={'library_pk': self.library.pk})


class GuestDeleteView(BaseDeleteView, LibraryOwnerTemplateView):
    model = UserProfile
    template_name = 'libraries/guest_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        guest: UserProfile = self.get_object()
        Lending.objects.filter(borrower=guest.home_library).update(is_completed=True, return_date=datetime.now())
        library = self.request.user.userprofile.home_library
        library.users.remove(guest)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
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

    def post(self, request):
        form = BookCopyForm({'book': request.POST['book'], 'library': self.library.pk})
        if form.is_valid():
            form.save()
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
            Q(book__title__contains=query) | Q(book__author__contains=query)
        ).order_by(
            'book__title'
        )
        return book_copies


class BookCopyDeleteView(BaseDeleteView, LibraryOwnerTemplateView):
    model = BookCopy
    template_name = 'libraries/book_copy_delete.html'

    def get_success_url(self):
        return reverse_lazy('library_details', kwargs={'library_pk': self.library.pk})


class BookCopyCommentUpdateView(BaseUpdateView, LibraryOwnerTemplateView):
    model = BookCopy
    fields = ('comment',)
    template_name = 'libraries/book_copy_comment.html'

    def get_success_url(self):
        return reverse_lazy('library_details', kwargs={'library_pk': self.library.pk})


class LendingCreateView(BaseCreateView, LibraryOwnerTemplateView):
    model = Lending
    fields = ('borrower',)
    template_name = 'libraries/lending_create.html'

    def test_func(self):
        if not super(LendingCreateView, self).test_func():
            return False

        book_copy = BookCopy.objects.get(pk=self.kwargs['pk'])
        try:
            Lending.objects.get(copy=book_copy, is_completed=False)
            return False
        except Lending.DoesNotExist:
            return True

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
        return HttpResponseRedirect(reverse_lazy('library_details', kwargs={'library_pk': self.library.pk}))

    def get_success_url(self):
        return reverse_lazy('library_details', kwargs={'library_pk': self.library.pk})


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
        lending.return_date = datetime.now()
        lending.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('library_details', kwargs={'library_pk': self.request.user.userprofile.home_library.pk})


class OutsideLendingCreateView(LibraryOwnerTemplateView):
    template_name = 'libraries/outside_lending_create.html'

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
        book_copy = BookCopy.objects.get(pk=self.kwargs['pk'])
        lending = Lending.objects.create(copy=book_copy, borrower=self.library)
        lending.save()
        return HttpResponseRedirect(reverse_lazy('library_details', kwargs={'library_pk': self.library.pk}))