from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:home")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        for i in range(10):
            Tweet.objects.create(author=self.user, text=f"Test {i+1}")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/home.html")

        # context内に含まれるツイートとDBのツイートが一致しているかどうか
        tweets_in_context = response.context["tweets"]
        tweets_in_db = Tweet.objects.all()
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

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        tweet_in_db = Tweet.objects.filter(author=valid_data["author"], text=valid_data["text"])
        self.assertTrue(tweet_in_db.exists())

    def test_failure_post_with_empty_content(self):
        invalid_data = {
            "author": self.user,
            "text": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        tweet_in_db = Tweet.objects.filter(author=invalid_data["author"], text=invalid_data["text"])
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
        self.assertEqual(response.status_code, 200)
        tweet_in_db = Tweet.objects.filter(author=invalid_data["author"], text=invalid_data["text"])
        self.assertFalse(tweet_in_db.exists())
        self.assertFalse(form.is_valid())
        self.assertIn("テキストは280文字以下で入力してください。", form.errors["text"])


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        for i in range(10):
            Tweet.objects.create(author=self.user, text=f"Test {i+1}")
        self.url = reverse("tweets:detail", kwargs={"pk": 1})

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        # context内に含まれるツイートとDBのツイートが一致しているかどうか
        tweets_in_context = response.context["tweet"]
        tweets_in_db = Tweet.objects.filter(pk=1)
        self.assertIn(tweets_in_context, tweets_in_db)


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        Tweet.objects.create(author=self.user, text="Test")

    def test_success_post(self):
        self.client.login(username="testuser", password="testpassword")
        self.url = reverse("tweets:delete", kwargs={"pk": 1})
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        tweet_in_db = Tweet.objects.filter(author=self.user, text="Test")
        self.assertFalse(tweet_in_db.exists())

    def test_failure_post_with_not_exist_tweet(self):
        self.client.login(username="testuser", password="testpassword")
        self.url = reverse("tweets:delete", kwargs={"pk": 2})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
        tweet_in_db = Tweet.objects.filter(author=self.user, text="Test")
        self.assertTrue(tweet_in_db.exists())

    def test_failure_post_with_incorrect_user(self):
        self.different_user = User.objects.create_user(username="different_user", password="differentpassword")
        self.client.login(username="different_user", password="differentpassword")
        self.url = reverse("tweets:delete", kwargs={"pk": 1})
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)
        tweet_in_db = Tweet.objects.filter(author=self.user, text="Test")
        self.assertTrue(tweet_in_db.exists())


# class TestLikeView(TestCase):
#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_liked_tweet(self):


# class TestUnLikeView(TestCase):

#     def test_success_post(self):

#     def test_failure_post_with_not_exist_tweet(self):

#     def test_failure_post_with_unliked_tweet(self):
