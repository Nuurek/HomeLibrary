from django.views.generic import TemplateView, FormView, RedirectView
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import timedelta

from .forms import SignUpForm
from .models import UserProfile
from libraries.models import Library


class SignUpView(FormView):
    template_name = 'accounts/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('mail_sent')

    def form_valid(self, form):
        user: User = form.save(commit=False)
        user.is_active = False
        user.save()
        user_profile = UserProfile(
            user=user, confirmation_code=get_random_string(32), registration_time=timezone.now())
        user_profile.save()
        # noinspection PyBroadException
        try:
            domain = get_current_site(self.request)
            user_profile.send_confirmation_code(domain=domain)
        except Exception:
            user.delete()

        return super().form_valid(form)


class ConfirmationView(TemplateView):
    template_name = 'accounts/confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile_id = kwargs['user_profile_id']
        confirmation_code = kwargs['code']
        user_profile = UserProfile.objects.get(id=user_profile_id)
        if user_profile.confirmation_code == confirmation_code:
            time_difference = timezone.now() - user_profile.registration_time
            if time_difference < timedelta(hours=24):
                user_profile.activate_user()
                Library.objects.create(owner=user_profile).save()
                context['success'] = True
                context['username'] = user_profile.user.username
            else:
                user_profile.user.delete()
                context['success'] = False
        else:
            context['success'] = False

        return context
