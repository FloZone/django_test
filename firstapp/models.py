import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.


class Author(AbstractUser):
    """
    User with default user fields and a timezone.
    """

    timezone = models.CharField(max_length=50, default='Europe/Paris')


class Message(models.Model):
    """
    Message with an author (user), a text and a publication date.
    """

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    message_text = models.CharField('message', max_length=140)
    publication_date = models.DateTimeField('publication date')

    def __str__(self):
        return str(self.publication_date) \
               + " " + str(self.message_text)

    def was_published_today(self):
        return self.publication_date >= timezone.now() - datetime.timedelta(days=1)

    was_published_today.admin_order_field = 'publication_date'
    was_published_today.boolean = True
    was_published_today.short_description = 'Published today?'
