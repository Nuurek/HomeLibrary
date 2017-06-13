from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Library


class LibraryView(LoginRequiredMixin, TemplateView):
    template_name = 'libraries/details.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['library_name'] = self.request.user.library.name
        return context


class LibraryUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'libraries/update.html'
    model = Library
    fields = ('name', )

    def get_object(self, queryset=None):
        return self.request.user.library
