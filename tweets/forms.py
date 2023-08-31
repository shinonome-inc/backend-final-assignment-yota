from django import forms

from .models import Tweet


class TweetForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = Tweet
        fields = ("text",)
