from django.conf.urls import url
from .views import LoginView, SignUpView


urlpatterns = [
    url(r'^$', LoginView.as_view(), name='login'),
    url(r'^sign_up$', SignUpView.as_view(), name='sign_up'),
]