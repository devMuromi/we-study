from .models import Thread
from django import forms


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ["title"]
