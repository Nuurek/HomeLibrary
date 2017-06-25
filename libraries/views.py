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
from django.db.models import F

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


class GuestDeleteView(DeleteView):
    model = UserProfile
    success_url = reverse_lazy('library_management')
    template_name = 'libraries/guest_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        library = self.request.user.userprofile.home_library
        library.users.remove(self.object)
        return HttpResponseRedirect(success_url)


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
            library=self.library
        ).filter(
            Q(book__title__contains=query) | Q(book__author__contains=query)
        )
        borrowed_book_copies = BookCopy.objects.filter(lending__borrower=self.library)
        return (book_copies | borrowed_book_copies).order_by('-book__title')


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
        print(lending)
        print(Lending.objects.all())
        return HttpResponseRedirect(reverse_lazy('library_details', kwargs={'library_pk': self.library.pk}))

    def get_success_url(self):
        return reverse_lazy('library_details', kwargs={'library_pk': self.library.pk})
