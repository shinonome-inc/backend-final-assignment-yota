from django.conf import settings
from django.db import models
from django.utils import timezone


class Tweet(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author")
    text = models.CharField(max_length=280)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Like", related_name="likes")

    def __str__(self):
        return self.text


class Like(models.Model):
    liking_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="liking_user")
    liked_tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="liked_tweet")

    class Meta:
        constraints = [
            # 重複するリレーションは登録できない
            models.UniqueConstraint(
                fields=["liking_user", "liked_tweet"],
                condition=models.Q(liking_user__isnull=False, liked_tweet__isnull=False),
                name="unique_like_relation",
                violation_error_message="同じツイートを複数回いいねすることはできません",
            ),
        ]
