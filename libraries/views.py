from django.views.generic import FormView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Library, Invitation
from .forms import SendInvitationForm


class LibraryDetailsView(LoginRequiredMixin, FormView):
    template_name = 'libraries/details.html'
    form_class = SendInvitationForm
    login_url = reverse_lazy('login')
    success_url = reverse_lazy('library_details')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        library = self.request.user.library
        context['library'] = library
        context['invitations'] = Invitation.objects.filter(library=library)
        return context

    def form_valid(self, form):
        invitation = Invitation(library=self.request.user.library, email=form.cleaned_data['email'])
        print(invitation)
        invitation.save()
        return super().form_valid(form)


class LibraryNameUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'libraries/update.html'
    model = Library
    fields = ('name', )

    def get_object(self, queryset=None):
        return self.request.user.library

    def form_valid(self, form):
        library = self.request.user.library
        library.is_name_default = False
        library.save()
        return super().form_valid(form)

