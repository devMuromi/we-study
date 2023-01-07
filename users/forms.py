from .models import User
from django.contrib.auth.forms import UserCreationForm

# from django.contrib.auth.models import User #에러남
from django import forms


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "gender", "birth_date", "password"]


# class LoginForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['email','password']
