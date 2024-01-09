from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .forms import TweetForm
from .models import Like, Tweet


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "tweets/home.html"
    queryset = Tweet.objects.select_related("author")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        tweets = context["object_list"]
        for tweet in tweets:
            tweet.is_liked = Like.objects.filter(liking_user=user, liked_tweet=tweet).exists()

        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    form_class = TweetForm
    template_name = "tweets/create.html"
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    model = Tweet
    queryset = Tweet.objects.select_related("author")
    template_name = "tweets/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        tweet = context["object"]
        tweet.is_liked = Like.objects.filter(liking_user=user, liked_tweet=tweet).exists()

        return context


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
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


class LikeView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        liked_tweet = get_object_or_404(Tweet, pk=pk)
        like_relation = Like.objects.filter(liking_user=request.user, liked_tweet=liked_tweet)

        if not like_relation.exists():
            Like.objects.create(liking_user=request.user, liked_tweet=liked_tweet)

        likes_count = liked_tweet.likes.count()

        return JsonResponse({"likes_count": likes_count})


class UnLikeView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        liked_tweet = get_object_or_404(Tweet, pk=pk)
        like_relation = Like.objects.filter(liking_user=request.user, liked_tweet=liked_tweet)

        if like_relation.exists():
            like_relation.delete()

        likes_count = liked_tweet.likes.count()

        return JsonResponse({"likes_count": likes_count})
