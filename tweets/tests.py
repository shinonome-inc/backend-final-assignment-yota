from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Like, Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        Tweet.objects.create(author=self.user, text="Test")

    def test_success_get(self):
        response = self.client.get(self.url)
        tweets_in_context = response.context["object_list"]
        tweets_in_db = Tweet.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/home.html")
        self.assertQuerysetEqual(tweets_in_context, tweets_in_db, ordered=False)


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:create")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        valid_data = {
            "author": self.user,
            "text": "Vanitas vanitatum, et omnia vanitas.",
        }

        response = self.client.post(self.url, valid_data)
        tweet_in_db = Tweet.objects.filter(author=valid_data["author"], text=valid_data["text"])

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(tweet_in_db.exists())

    def test_failure_post_with_empty_content(self):
        invalid_data = {
            "author": self.user,
            "text": "",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        tweet_in_db = Tweet.objects.filter(author=invalid_data["author"], text=invalid_data["text"])

        self.assertEqual(response.status_code, 200)
        self.assertFalse(tweet_in_db.exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["text"])

    def test_failure_post_with_too_long_content(self):
        invalid_data = {
            "author": self.user,
            "text": "a" * 281,
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        tweet_in_db = Tweet.objects.filter(author=invalid_data["author"], text=invalid_data["text"])

        self.assertEqual(response.status_code, 200)
        self.assertFalse(tweet_in_db.exists())
        self.assertFalse(form.is_valid())
        self.assertIn("この値は 280 文字以下でなければなりません( 281 文字になっています)。", form.errors["text"])


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(author=self.user, text="Test")
        self.url = reverse("tweets:detail", kwargs={"pk": self.tweet.id})

    def test_success_get(self):
        response = self.client.get(self.url)
        tweets_in_context = response.context["tweet"]
        tweets_in_db = Tweet.objects.filter(pk=self.tweet.id)

        self.assertEqual(response.status_code, 200)
        self.assertIn(tweets_in_context, tweets_in_db)


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(author=self.user, text="Test")

    def test_success_post(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse("tweets:delete", kwargs={"pk": self.tweet.id})

        response = self.client.post(url)
        tweet_in_db = Tweet.objects.filter(author=self.user, text="Test")

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(tweet_in_db.exists())

    def test_failure_post_with_not_exist_tweet(self):
        self.client.login(username="testuser", password="testpassword")
        url = reverse("tweets:delete", kwargs={"pk": 2})

        response = self.client.post(url)
        tweet_in_db = Tweet.objects.filter(author=self.user, text="Test")

        self.assertEqual(response.status_code, 404)
        self.assertTrue(tweet_in_db.exists())

    def test_failure_post_with_incorrect_user(self):
        User.objects.create_user(username="different_user", password="differentpassword")
        self.client.login(username="different_user", password="differentpassword")
        url = reverse("tweets:delete", kwargs={"pk": self.tweet.id})

        response = self.client.post(url)
        tweet_in_db = Tweet.objects.filter(author=self.user, text="Test")

        self.assertEqual(response.status_code, 403)
        self.assertTrue(tweet_in_db.exists())


class TestLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(author=self.user, text="Test")

    def test_success_post(self):
        url = reverse("tweets:like", kwargs={"pk": self.tweet.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(liking_user=self.user).exists())

    def test_failure_post_with_not_exist_tweet(self):
        url = reverse("tweets:like", kwargs={"pk": 2})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Like.objects.filter(liking_user=self.user).exists())

    def test_failure_post_with_liked_tweet(self):
        url = reverse("tweets:like", kwargs={"pk": self.tweet.id})
        Like.objects.create(liking_user=self.user, liked_tweet=self.tweet)
        initial_like_count = Like.objects.count()

        response = self.client.post(url)
        updated_like_count = Like.objects.count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(initial_like_count, updated_like_count)


class TestUnLikeView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(author=self.user, text="Test")
        Like.objects.create(liking_user=self.user, liked_tweet=self.tweet)

    def test_success_post(self):
        url = reverse("tweets:unlike", kwargs={"pk": self.tweet.id})
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Like.objects.filter(liking_user=self.user).exists())

    def test_failure_post_with_not_exist_tweet(self):
        url = reverse("tweets:unlike", kwargs={"pk": 2})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Like.objects.filter(liking_user=self.user).exists())

    def test_failure_post_with_unliked_tweet(self):
        url = reverse("tweets:unlike", kwargs={"pk": self.tweet.id})
        self.client.post(url)

        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
