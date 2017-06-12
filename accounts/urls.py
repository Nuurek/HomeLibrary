from django.conf.urls import url
from django.views.generic import TemplateView
from .views import LoginView, SignUpView, ConfirmationView


urlpatterns = [
    url(r'^$', LoginView.as_view(), name='login'),
    url(r'^sign_up$', SignUpView.as_view(), name='sign_up'),
    url(r'^mail_sent$', TemplateView.as_view(template_name='mail_sent.html'), name='mail_sent'),
    url(r'^confirmation/(?P<user_profile_id>[0-9]+)/(?P<code>.{32})/$',
        ConfirmationView.as_view(), name='confirmation'),
]
