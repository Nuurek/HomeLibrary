from django.conf.urls import url, include
from django.contrib import admin

from libraries import urls as library_urls
from accounts import urls as accounts_urls


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(accounts_urls)),
]
