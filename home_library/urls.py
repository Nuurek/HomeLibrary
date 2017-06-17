from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView

from accounts import urls as account_urls
from libraries import urls as library_urls
from books import urls as book_urls


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='home.html'), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^account/', include(account_urls)),
    url(r'^library/', include(library_urls)),
    url(r'^book/', include(book_urls)),
]
