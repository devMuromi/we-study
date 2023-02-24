from .models import Thread, Post
from django import forms


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ["title"]


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["content", "is_anonymous"]
