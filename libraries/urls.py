from django.conf.urls import url

from .views import LibraryDetailsView, LibraryNameUpdateView, InvitationConfirmationView


urlpatterns = [
    url(r'^details$', LibraryDetailsView.as_view(), name='library_details'),
    url(r'^update', LibraryNameUpdateView.as_view(), name='library_name_update'),
    url(r'^confirm_invitation/(?P<library_id>[0-9]+)/(?P<code>.{32})/$', InvitationConfirmationView.as_view(),
        name='invitation_confirmation'),
]