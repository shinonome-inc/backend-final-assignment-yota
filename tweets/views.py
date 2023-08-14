from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, TemplateView

User = get_user_model()


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "tweets/home.html"


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User  # ユーザーモデルを指定
    template_name = "tweets/home.html"
    context_object_name = "user"  # テンプレート内で使用する変数名

    def get_object(self):
        return User.objects.get(username=self.request.user)
