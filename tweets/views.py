from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, TemplateView

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
