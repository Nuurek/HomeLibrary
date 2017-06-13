from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Library


class LibraryView(LoginRequiredMixin, TemplateView):
    template_name = 'libraries/details.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['library'] = self.request.user.library
        return context


class LibraryUpdateView(LoginRequiredMixin, UpdateView):
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

