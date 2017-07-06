from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.template.loader import render_to_string


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    confirmation_code = models.CharField(max_length=32, null=True)
    registration_time = models.DateTimeField(null=True)

    def __str__(self):
        return self.user.username + ', ' + ('active' if self.user.is_active else 'not active')

    def send_confirmation_code(self, domain):
        subject = "Home Library Email Verification"
        message = render_to_string('accounts/confirmation_mail.html', {
            'domain': domain,
            'username': self.user.username,
            'link': reverse('confirmation', kwargs={
                'user_profile_id': self.id,
                'code': self.confirmation_code,
            })
        })
        self.user.email_user(subject, message)
        print("Sent confirmation code to " + self.user.username)

    def activate_user(self):
        self.user.is_active = True
        self.user.save()
        print("Activated account for " + self.user.username)

    def books_per_month(self):
        books_read = self.reading_set.filter(is_completed=True).count()
        period = self.get_period_since_join()
        months = int(period.days / 30.4 + 1)
        return books_read / months

    def pages_per_day(self):
        key = 'copy__book__page_count'
        pages = self.reading_set.filter(is_completed=True).aggregate(Sum(key))[key + '__sum']
        if pages:
            period = self.get_period_since_join()
            return int(pages / period.days)
        else:
            return 0

    def last_read_book(self):
        return self.reading_set.filter(is_completed=True).order_by('-end_date').first()

    def currently_read_books(self):
        return self.reading_set.filter(is_completed=False).all().select_related('copy')

    def lent_books(self):
        return self.home_library.bookcopy_set.filter(lending__is_completed=False)

    def get_period_since_join(self):
        return timezone.now() - self.user.date_joined
