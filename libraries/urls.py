from django.conf.urls import url

from .views import (LibraryDetailsView, LibraryNameUpdateView, InvitationConfirmationView, InvitationDeleteView,
                    GuestDeleteView, LibrariesListView)


urlpatterns = [
    url(r'^management$', LibraryDetailsView.as_view(), name='library_management'),
    url(r'^update', LibraryNameUpdateView.as_view(), name='library_name_update'),
    url(r'^list', LibrariesListView.as_view(), name='library_list'),
    url(r'^confirm_invitation/(?P<library_id>[0-9]+)/(?P<code>.{32})/$', InvitationConfirmationView.as_view(),
        name='invitation_confirmation'),
    url(r'^invitation_delete/(?P<pk>[0-9]+)', InvitationDeleteView.as_view(), name='invitation_delete'),
    url(r'^guest_delete/(?P<pk>[0-9]+)', GuestDeleteView.as_view(), name='guest_delete'),
]