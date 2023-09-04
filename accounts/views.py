from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView

from accounts.models import FollowRelation
from mysite.settings import LOGIN_REDIRECT_URL
from tweets.models import Tweet

from .forms import SignupForm

User = get_user_model()


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy(LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


class UserProfileView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "accounts/profile.html"
    paginate_by = 10

    def get_queryset(self):
        username = self.kwargs.get("username")
        self.user = get_object_or_404(User, username=username)
        return Tweet.objects.select_related("author").filter(author=self.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["target_user"] = self.user
        context["following"] = [following.following_user for following in self.user.following.all()]
        context["followed"] = [followed.following_user for followed in self.user.followed.all()]

        return context


class FollowView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"

    def post(self, request, username):
        following = request.user
        followed = get_object_or_404(User, username=username)

        follow_relation = FollowRelation(following_user=following, followed_user=followed)

        try:
            follow_relation.clean_same_person()
            follow_relation.clean_duplication()
        except ValidationError as e:
            print(e)
            return redirect(reverse("tweets:home"))

        follow_relation.save()

        return redirect(reverse("tweets:home"))


class UnFollowView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"

    def post(self, request, username):
        following = request.user
        followed = get_object_or_404(User, username=username)

        follow_relation = FollowRelation.objects.filter(following_user=following, followed_user=followed)
        follow_relation.delete()

        return redirect(reverse("tweets:home"))
