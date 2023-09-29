from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.forms import ValidationError
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .forms import TweetForm
from .models import Like, Tweet


class HomeView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "tweets/home.html"
    queryset = Tweet.objects.select_related("author")


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
    template_name = "tweets/home.html"

    def post(self, request, pk):
        liking_user = request.user
        liked_tweet = get_object_or_404(Tweet, pk=pk)
        like_relation = Like(liking_user=liking_user, liked_tweet=liked_tweet)

        try:
            like_relation.full_clean()
        except ValidationError as e:
            return HttpResponseBadRequest(e.messages)

        like_relation.save()

        return HttpResponseRedirect(reverse("tweets:home"))
