from django.conf.urls import url

from .views import LibraryDetailsView, LibraryNameUpdateView


urlpatterns = [
    url(r'^details$', LibraryDetailsView.as_view(), name='library_details'),
    url(r'^update', LibraryNameUpdateView.as_view(), name='library_name_update'),
]