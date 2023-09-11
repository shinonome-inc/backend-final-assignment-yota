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

    class Meta:
        constraints = [
            # 重複するリレーションは登録できない
            models.UniqueConstraint(fields=["following_user", "followed_user"], name="unique_relation"),
            # 自分自身をフォローすることはできない
            models.CheckConstraint(
                check=~models.Q(following_user=models.F("followed_user")), name="cannot_follow_myself"
            ),
        ]

    def clean_same_person(self):
        if self.followed_user == self.following_user:
            raise ValidationError("自分自身をフォローすることはできない")

    def clean_duplication(self):
        # 同じユーザーを複数回フォローできないように制約を追加
        duplicate_relations = FollowRelation.objects.filter(
            following_user=self.following_user, followed_user=self.followed_user
        )
        if duplicate_relations.exists():
            raise ValidationError("同じユーザーを複数回フォローすることはできません")
