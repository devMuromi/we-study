from django.urls import path, include
from . import views
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path("signup/", views.signUp, name="signUp"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("found/", views.found, name="found"),
    path("idfound/", views.idfound, name="idfound"),
    path("pwfound/", views.pwfound, name="pwfound"),
]
