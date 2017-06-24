from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import send_mail

from accounts.models import UserProfile
from books.models import Book


class Library(models.Model):
    name = models.CharField(max_length=40, null=False, default="Home Library")
    is_name_default = models.BooleanField(default=True)
    owner = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True, related_name='home_library')
    users = models.ManyToManyField(UserProfile, related_name='libraries', blank=True)

    class Meta:
        verbose_name_plural = 'libraries'

    def get_absolute_url(self):
        return reverse('library_management', kwargs={'library_pk': self.pk})

    def __str__(self):
        return self.name + " of the " + self.owner.user.username


class Invitation(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    email = models.EmailField(null=False)
    confirmation_code = models.CharField(max_length=32, null=True)

    class Meta:
        unique_together = ('library', 'email')

    def send_invitation_email(self, domain):
        subject = "Home Library invitation mail"
        message = render_to_string('libraries/invitation_mail.html', {
            'username': self.email.split('@')[0],
            'owner': self.library.owner.user.username,
            'library': self.library.name,
            'domain': domain,
            'link': reverse('invitation_confirmation', kwargs={
                'library_id': self.library.pk,
                'code': self.confirmation_code,
            }),
        })
        send_mail(subject, message, self.library.owner.user.email, [self.email, ])

    def __str__(self):
        return "Invitation to " + self.library.name + " for " + self.email


class BookCopy(models.Model):
    book = models.ForeignKey(Book)
    library = models.ForeignKey(Library)
    comment = models.TextField(max_length=200, blank=True)

    def __str__(self):
        return str(self.book) + ' in ' + str(self.library)


class Lending(models.Model):
    copy = models.ForeignKey(BookCopy)
    borrower = models.ForeignKey(Library, blank=True, null=True)
    lend_date = models.DateTimeField(auto_now=True)
    return_date = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        lender_name = self.copy.library.owner.user.username
        title = self.copy.book.title
        borrower_name = self.borrower.owner.user.username
        return lender_name + "'s " + title + ' lend to ' + borrower_name
