from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import send_mail
from datetime import datetime

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
                'library_pk': self.library.pk,
                'code': self.confirmation_code,
            }),
        })
        send_mail(subject, message, self.library.owner.user.email, [self.email, ])

    def __str__(self):
        return "Invitation to " + self.library.name + " for " + self.email


class BookCopy(models.Model):
    book = models.ForeignKey(Book)
    library = models.ForeignKey(Library, null=True, blank=True)
    comment = models.TextField(max_length=200, blank=True)

    def __str__(self):
        return str(self.book) + ' in ' + str(self.library)

    def is_kept_by(self, user_profile: UserProfile):
        if not self.library:
            return True
        is_owner = self.library.owner == user_profile
        is_lent = Lending.objects.filter(copy=self, is_completed=False).exists()
        return (
            (is_owner and not is_lent) or
            (Lending.objects.filter(copy=self, borrower=user_profile.home_library, is_completed=False))
        )


class Lending(models.Model):
    copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE)
    borrower = models.ForeignKey(Library, blank=True, null=True)
    lend_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        lender_name = self.copy.library.owner.user.username if self.copy.library else "Anonym"
        title = self.copy.book.title
        borrower_name = self.borrower.owner.user.username if self.borrower else "Anonym"
        date = datetime.date(self.lend_date)
        date = date.strftime('%d.%m.%Y')
        full_name = lender_name + "'s " + '"' + title + '" lent to ' + borrower_name + " on " + date
        return ("[COMPLETED] " if self.is_completed else '') + full_name


class Reading(models.Model):
    copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE)
    reader = models.ForeignKey(UserProfile)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        reader_name = self.reader.user.username
        title = self.copy.book.title
        full_name = title + ' read by ' + reader_name
        return "[" + ("COMPLETED" if self.is_completed else self.start_date.strftime('%d.%m.%Y')) + "]" + full_name
