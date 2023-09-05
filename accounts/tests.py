from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import FollowRelation
from tweets.models import Tweet

User = get_user_model()


class TestSignupView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")
        self.user = User.objects.create_user(username="tester", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, valid_data)

        # 1の確認 = LOGIN_REDIRECT_URLにリダイレクトすること
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        # 2の確認 = ユーザーが作成されること
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        # 3の確認 = ログイン状態になること
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])
        self.assertIn("このフィールドは必須です。", form.errors["email"])
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_empty_username(self):
        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])

    def test_failure_post_with_empty_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["email"])

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_duplicated_user(self):
        invalid_data = {
            "username": "tester",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                username=invalid_data["username"], email=invalid_data["email"], password=invalid_data["password2"]
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])

    def test_failure_post_with_invalid_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "testtest.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("有効なメールアドレスを入力してください。", form.errors["email"])

    def test_failure_post_with_too_short_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "tstpwd",
            "password2": "tstpwd",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは短すぎます。最低 8 文字以上必要です。", form.errors["password2"])

    def test_failure_post_with_password_similar_to_username(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testuser",
            "password2": "testuser",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは ユーザー名 と似すぎています。", form.errors["password2"])

    def test_failure_post_with_only_numbers_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "27182818",
            "password2": "27182818",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは数字しか使われていません。", form.errors["password2"])

    def test_failure_post_with_mismatch_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testuser",
            "password2": "helloworld",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username=invalid_data["username"]).exists())
        self.assertFalse(form.is_valid())
        self.assertIn("確認用パスワードが一致しません。", form.errors["password2"])


class TestLoginView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:login")
        self.user = User.objects.create_user(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "password": "testpassword",
        }

        response = self.client.post(self.url, valid_data)

        # 1の確認 = LOGIN_REDIRECT_URLにリダイレクトすること
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        invalid_data = {
            "username": "NotUser",
            "password": "testpassword",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertIn("正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。", form.errors["__all__"])
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "password": "",
        }

        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["password"])
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:logout")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_success_post(self):
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.follow = User.objects.create_user(username="follow", password="testpassword")
        self.follower_1 = User.objects.create_user(username="follower1", password="testpassword")
        self.follower_2 = User.objects.create_user(username="follower2", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        self.url = reverse("accounts:profile", kwargs={"username": "testuser"})
        Tweet.objects.create(author=self.user, text="Test")
        FollowRelation.objects.create(following_user=self.user, followed_user=self.follow)
        FollowRelation.objects.create(following_user=self.follower_1, followed_user=self.user)
        FollowRelation.objects.create(following_user=self.follower_2, followed_user=self.user)

    def test_success_get(self):
        response = self.client.get(self.url)
        tweets_in_context = response.context["tweet_list"]
        following_count = response.context["following_count"]
        followed_count = response.context["followed_count"]
        tweets_in_db = Tweet.objects.filter(author=self.user)
        following_count_in_db = FollowRelation.objects.filter(following_user=self.user).count()
        followed_count_in_db = FollowRelation.objects.filter(followed_user=self.user).count()

        # context内に含まれるツイートとDBのツイートが一致しているかどうか
        self.assertQuerysetEqual(tweets_in_context, tweets_in_db, ordered=False)
        # context内に含まれるフォロー数とフォロワー数がDBに保存されている該当のユーザーのフォロー数とフォロワー数に同一であるか
        self.assertEqual(following_count, following_count_in_db)
        self.assertEqual(followed_count, followed_count_in_db)


# class TestUserProfileEditView(TestCase):
#     def test_success_get(self):

#     def test_success_post(self):

#     def test_failure_post_with_not_exists_user(self):

#     def test_failure_post_with_incorrect_user(self):


class TestFollowView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.follow = User.objects.create_user(username="follow", password="testpassword")
        self.url = reverse("accounts:follow", kwargs={"username": self.follow.username})
        self.client.login(username="testuser", password="testpassword")

    def test_success_post(self):
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(FollowRelation.objects.filter(following_user=self.user).exists())

    def test_failure_post_with_not_exist_user(self):
        not_exist_url = reverse("accounts:follow", kwargs={"username": "NotUser"})
        response = self.client.post(not_exist_url)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(FollowRelation.objects.filter(following_user=self.user).exists())

    def test_failure_post_with_self(self):
        myself_url = reverse("accounts:follow", kwargs={"username": self.user.username})
        response = self.client.post(myself_url)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(FollowRelation.objects.filter(following_user=self.user).exists())


class TestUnFollowView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.follow = User.objects.create_user(username="follow", password="testpassword")
        self.url = reverse("accounts:unfollow", kwargs={"username": self.follow.username})
        self.client.login(username="testuser", password="testpassword")
        FollowRelation.objects.create(following_user=self.user, followed_user=self.follow)

    def test_success_post(self):
        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(FollowRelation.objects.filter(following_user=self.user).exists())

    def test_failure_post_with_not_exist_user(self):
        not_exist_url = reverse("accounts:unfollow", kwargs={"username": "NotUser"})
        response = self.client.post(not_exist_url)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(FollowRelation.objects.filter(following_user=self.user).exists())

    def test_failure_post_with_self(self):
        myself_url = reverse("accounts:unfollow", kwargs={"username": self.user.username})
        response = self.client.post(myself_url)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(FollowRelation.objects.filter(following_user=self.user).exists())


class TestFollowingListView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.url = reverse("accounts:following_list", kwargs={"username": self.user.username})
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class TestFollowerListView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.url = reverse("accounts:follower_list", kwargs={"username": self.user.username})
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
