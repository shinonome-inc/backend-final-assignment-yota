from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView

from .forms import TweetForm
from .models import Tweet

User = get_user_model()


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "tweets/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tweets"] = Tweet.objects.all()
        return context


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User  # ユーザーモデルを指定
    template_name = "tweets/home.html"
    context_object_name = "user"  # テンプレート内で使用する変数名

    def get_object(self):
        return User.objects.get(username=self.request.user)


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    form_class = TweetForm
    template_name = "tweets/create.html"
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        tweet = form.save(commit=False)
        tweet.author = self.request.user
        tweet.published_date = timezone.now()
        tweet = form.save()
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        messages.success(self.request, "記事を投稿しました。")
        return reverse("tweets:home")
