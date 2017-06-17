from django.contrib import admin

from .models import Book, GoogleBook, BookCopy


admin.site.register(Book)
admin.site.register(GoogleBook)
admin.site.register(BookCopy)
