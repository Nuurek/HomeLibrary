from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=50)


class GoogleBook(models.Model):
    google_id = models.CharField(max_length=12)
    ISBN = models.CharField(max_length=13)
    ebook_link = models.URLField()


class Book(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    page_count = models.IntegerField()
    author = models.CharField(max_length=50)
    cover = models.ImageField()
    google_info = models.OneToOneField(GoogleBook, null=True)


class BookCopy(models.Model):
    book = models.ForeignKey(Book)
