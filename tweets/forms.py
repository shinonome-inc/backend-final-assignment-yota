from django import forms

from .models import Tweet


class TweetForm(forms.ModelForm):
    class Meta:
        model = Tweet
        fields = ("text",)

    def clean_text(self):
        text = self.cleaned_data["text"]
        if len(text) > 280:
            raise forms.ValidationError("テキストは280文字以下で入力してください。")
        return text
