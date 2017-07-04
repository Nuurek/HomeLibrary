from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from accounts.models import UserProfile
from libraries.models import BookCopy


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        profile: UserProfile = self.request.user.userprofile
        context['books_per_month'] = profile.books_per_month()
        context['pages_per_day'] = profile.pages_per_day()
        context['last_read_book'] = profile.last_read_book()
        context['currently_read_books'] = profile.currently_read_books()
        context['lent_books'] = profile.lent_books()
        context['borrowed_books'] = BookCopy.objects.filter(
            lending__borrower=profile.home_library, lending__is_completed=False
        )
        return context
