from .models import Studyroom, Study
from django import forms


class StudyroomForm(forms.ModelForm):
    class Meta:
        model = Studyroom
        fields = ["name", "description"]


class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ["content", "learning_time", "progress"]
