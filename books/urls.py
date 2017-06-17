from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r'create', BookCopyCreateView.as_view(), name='book_copy_create'),
]