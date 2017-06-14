from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import send_mail

from accounts.models import UserProfile


class Library(models.Model):
    name = models.CharField(max_length=40, null=False, default="Home Library")
    is_name_default = models.BooleanField(default=True)
    owner = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True, related_name='home_library')
    users = models.ManyToManyField(UserProfile, related_name='libraries', blank=True)

    class Meta:
        verbose_name_plural = 'libraries'

    @staticmethod
    def get_absolute_url():
        return reverse('library_details')

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
