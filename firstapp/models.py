import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.


class Message(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
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


class Answer(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    answer_text = models.CharField('message', max_length=140)
    publication_date = models.DateTimeField('publication date')

    def __str__(self):
        return str(self.message.id) \
               + str(self.publication_date) \
               + " " + str(self.answer_text)

    def was_published_today(self):
        return self.publication_date >= timezone.now() - datetime.timedelta(days=1)

    was_published_today.admin_order_field = 'publication_date'
    was_published_today.boolean = True
    was_published_today.short_description = 'Published today?'
