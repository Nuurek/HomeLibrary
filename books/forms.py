from django.forms import ModelForm

from .models import Book


class BookForm(ModelForm):

    class Meta:
        model = Book
        fields = ('title', 'description', 'page_count', 'author', 'cover')


class BookPreviewForm(ModelForm):

    class Meta:
        model = Book
        fields = ('title', 'description', 'page_count', 'author')
