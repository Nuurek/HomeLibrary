from django.conf.urls import url

from .views import LibraryView, LibraryUpdateView


urlpatterns = [
    url(r'^details$', LibraryView.as_view(), name='library_details'),
    url(r'^update', LibraryUpdateView.as_view(), name='library_update'),
]