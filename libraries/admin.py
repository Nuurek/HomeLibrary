from django.contrib import admin

from .models import Library, BookCopy, Invitation, Lending, Reading


admin.site.register(Library)
admin.site.register(BookCopy)
admin.site.register(Invitation)
admin.site.register(Lending)
admin.site.register(Reading)
