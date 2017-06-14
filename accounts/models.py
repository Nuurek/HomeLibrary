from django.db import models
from django.urls import reverse
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

    def activate_user(self):
        self.user.is_active = True
        self.user.save()
