from django.db import models


from accounts.models import UserProfile
from libraries.models import Library


class Book(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1500)
    page_count = models.PositiveSmallIntegerField()
    author = models.CharField(max_length=50)
    cover = models.ImageField(upload_to='cover/', blank=True)

    class Meta:
        unique_together = ('title', 'author')

    def __str__(self):
        return self.title + ', ' + self.author


class BookCopy(models.Model):
    book = models.ForeignKey(Book)
    library = models.ForeignKey(Library)

    def __str__(self):
        return str(self.book) + ' in ' + str(self.library)


class BookCoverPreview(models.Model):
    cover = models.ImageField()
    profile = models.ForeignKey(UserProfile)
