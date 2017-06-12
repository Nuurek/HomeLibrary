from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string

from .forms import SignUpForm
from .models import UserProfile


class LoginView(TemplateView):
    template_name = 'login.html'


class SignUpView(FormView):
    template_name = 'signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('mail_sent')

    def form_valid(self, form):
        user: User = form.save()
        user.set_password(user.password)
        user.is_active = False
        user.save()
        user_profile = UserProfile(
            user=user, confirmation_code=get_random_string(32))
        user_profile.save()
        # noinspection PyBroadException
        try:
            domain = get_current_site(self.request)
            user_profile.send_confirmation_code(domain=domain)
        except Exception:
            user.delete()

        return super().form_valid(form)


class ConfirmationView(TemplateView):
    template_name = 'confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile_id = kwargs['user_profile_id']
        print()
        confirmation_code = kwargs['code']
        user_profile = UserProfile.objects.get(id=user_profile_id)
        print(user_profile.confirmation_code)
        print(confirmation_code)
        if user_profile.confirmation_code == confirmation_code:
            user_profile.activate_user()
            context['success'] = True
            context['username'] = user_profile.user.username
        else:
            context['success'] = False

        return context
