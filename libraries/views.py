from django.views.generic import FormView, UpdateView, TemplateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404

from .models import Library, Invitation
from .forms import SendInvitationForm
from accounts.models import UserProfile


class LibraryGuestMixin(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    pk_url_kwarg = 'library_pk'
    raise_exception = True
    library = None

    def dispatch(self, request, *args, **kwargs):
        library_pk = self.kwargs['library_pk']
        self.library = get_object_or_404(Library, pk=library_pk)
        return super(LibraryGuestMixin, self).dispatch(request, *args, **kwargs)

    def test_func(self):
        profile = self.request.user.userprofile
        return profile == self.library.owner or profile in self.library.users.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['library_pk'] = self.library.pk
        return context


class LibraryDetailsView(LibraryGuestMixin):
    template_name = 'libraries/details.html'


class LibraryManagementView(LoginRequiredMixin, FormView):
    template_name = 'libraries/management.html'
    form_class = SendInvitationForm
    login_url = reverse_lazy('login')
    success_url = reverse_lazy('library_management')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        library = self.request.user.userprofile.home_library
        context['library'] = library
        context['guests'] = library.users.all()
        context['invitations'] = Invitation.objects.filter(library=library)
        return context

    def form_valid(self, form):
        invitation = Invitation(library=self.request.user.userprofile.home_library, email=form.cleaned_data['email'],
                                confirmation_code=get_random_string(32))
        invitation.save()
        domain = get_current_site(self.request)
        invitation.send_invitation_email(domain)
        return super().form_valid(form)


class LibraryNameUpdateView(LoginRequiredMixin, UpdateView):
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
        library_id = kwargs['library_id']
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


class InvitationDeleteView(DeleteView):
    model = Invitation
    success_url = reverse_lazy('library_management')


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