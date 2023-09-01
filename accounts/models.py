from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.forms import ValidationError
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField()
    follow = models.ManyToManyField(
        "User",
        through="FollowRelation",
    )


class FollowRelation(models.Model):
    following_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="following")
    followed_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="followed")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def clean_relation(self):
        if self.followed_user == self.following_user:
            raise ValidationError("自分自身をフォローすることはできない")
