from django.contrib import admin

from .models import Book, BookCopy, BookCoverPreview


admin.site.register(Book)
admin.site.register(BookCopy)
admin.site.register(BookCoverPreview)
