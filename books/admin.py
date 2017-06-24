from django.contrib import admin

from .models import Book, BookCoverPreview
from libraries.models import BookCopy

admin.site.register(Book)
admin.site.register(BookCopy)
admin.site.register(BookCoverPreview)
