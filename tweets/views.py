from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .forms import TweetForm
from .models import Tweet


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "tweets/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # プリロードしてN+1回避
        context["tweets"] = Tweet.objects.select_related("author").all()
        return context


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


class TweetDetailView(LoginRequiredMixin, DetailView):
    model = Tweet
    queryset = Tweet.objects.select_related("author")
    template_name = "tweets/detail.html"


class TweetDeleteView(UserPassesTestMixin, DeleteView):
    model = Tweet
    queryset = Tweet.objects.select_related("author")
    template_name = "tweets/delete.html"
    success_url = reverse_lazy("tweets:home")

    def get(self, request, *args, **kwargs):
        # test_funcの方が先に呼ばれるので、getメソッド内でself.objectにアクセス可能
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def test_func(self):
        self.object = self.get_object()
        return self.object.author == self.request.user
