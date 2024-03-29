# Generated by Django 4.1.10 on 2023-09-27 07:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tweets", "0002_rename_tweets_tweet_text"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tweet",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="author", to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.CreateModel(
            name="Like",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "liked_tweet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="liked_tweet", to="tweets.tweet"
                    ),
                ),
                (
                    "liking_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="liking_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="tweet",
            name="likes",
            field=models.ManyToManyField(related_name="likes", through="tweets.Like", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddConstraint(
            model_name="like",
            constraint=models.UniqueConstraint(
                condition=models.Q(("liked_tweet__isnull", False), ("liking_user__isnull", False)),
                fields=("liking_user", "liked_tweet"),
                name="unique_like_relation",
                violation_error_message="同じツイートを複数回いいねすることはできません",
            ),
        ),
    ]
