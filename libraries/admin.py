from django.contrib import admin

from .models import Library, BookCopy, Invitation, Lending


admin.site.register(Library)
admin.site.register(BookCopy)
admin.site.register(Invitation)
admin.site.register(Lending)
