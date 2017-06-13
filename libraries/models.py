from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Library(models.Model):
    name = models.CharField(max_length=40, null=False)
    is_name_default = models.BooleanField(default=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        verbose_name_plural = 'libraries'

    @staticmethod
    def get_absolute_url():
        return reverse('library_details')

    def __str__(self):
        return self.name + ' of the ' + self.owner.username
