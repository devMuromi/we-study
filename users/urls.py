from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.sign_up, name="signUp"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("found/", views.found, name="found"),
    path("foundid/", views.found_id, name="foundId"),
    path("foundpassword/", views.found_password, name="foundPassword"),
]
