from django.conf import settings
from django.db import models
from django.utils import timezone


class Tweet(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.CharField(max_length=280)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.text
