from django.conf.urls import url, include

from .views import *
from books import urls as book_urls
from books.views import BookListView


urlpatterns = [
    url(r'^$', LibraryDetailsView.as_view(), name='library_details'),
    url(r'^management$', LibraryManagementView.as_view(), name='library_management'),
    url(r'^update', LibraryNameUpdateView.as_view(), name='library_name_update'),
    url(r'^list', LibrariesListView.as_view(), name='library_list'),
    url(r'^confirm_invitation/(?P<code>.{32})/$', InvitationConfirmationView.as_view(),
        name='invitation_confirmation'),
    url(r'^invitation_delete/(?P<pk>[0-9]+)', InvitationDeleteView.as_view(), name='invitation_delete'),
    url(r'^guest_delete/(?P<pk>[0-9]+)', GuestDeleteView.as_view(), name='guest_delete'),
    url(r'^copy/list$', BookCopiesListView.as_view(), name='library_book_copies'),
    url(r'^copy/create$', BookCopyCreateView.as_view(), name='book_copy_create'),
    url(r'^copy/delete/(?P<pk>[0-9]+)$', BookCopyDeleteView.as_view(), name='book_copy_delete'),
    url(r'^copy/comment/(?P<pk>[0-9]+)$', BookCopyCommentUpdateView.as_view(), name='book_copy_comment'),
    url(r'^copy/create/', include(book_urls)),
    url(r'^copy/(?P<pk>[0-9]+)/lend$', LendingCreateView.as_view(), name='lending_create'),
    url(r'^copy/(?P<pk>[0-9]+)/return$', LendingDeleteView.as_view(), name='lending_delete'),
    url(r'^outside_lending$', OutsideLendingCreateView.as_view(), name='outside_lending_create'),
    url(r'^outside_lending/list$', BookListView.as_view()),
    url(r'^outside_lending/(?P<pk>[0-9]+)$', OutsideLendingConfirmView.as_view(), name='outside_lending_confirm'),
]
