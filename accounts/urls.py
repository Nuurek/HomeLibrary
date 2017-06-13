from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from .views import LoginView, LogoutView, SignUpView, ConfirmationView


urlpatterns = [
    url(r'^log_in$', auth_views.login, {'template_name': 'accounts/login.html'}, name='login'),
    url(r'^log_out', auth_views.logout, {'next_page': 'home'}, name='logout'),
    url(r'^sign_up$', SignUpView.as_view(), name='sign_up'),
    url(r'^mail_sent$', TemplateView.as_view(template_name='accounts/mail_sent.html'), name='mail_sent'),
    url(r'^confirmation/(?P<user_profile_id>[0-9]+)/(?P<code>.{32})/$',
        ConfirmationView.as_view(), name='confirmation'),
]
