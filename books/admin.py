from django.contrib import admin

from .models import Book, BookCoverPreview


admin.site.register(Book)
admin.site.register(BookCoverPreview)
