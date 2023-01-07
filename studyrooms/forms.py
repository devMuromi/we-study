from .models import Studyroom, Todo
from django import forms


class StudyroomForm(forms.ModelForm):
    class Meta:
        model = Studyroom
        fields = ["studyroom_name", "studyroom_classification"]


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ["content", "learning_time", "progress"]
