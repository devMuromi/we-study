from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth.models import User
from django.contrib import auth
from .forms import *
from django.conf import settings


def sign_up(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            auth.login(request, user)
            return redirect("/")
        else:
            return render(request, "auth/signup.html")
    elif request.method == "GET":
        if request.user.is_authenticated:
            return redirect("main")
        else:
            form = UserForm()
            return render(request, "auth/signup.html")


def login(request):
    if request.method == "POST":
        # form = LoginForm(request.POST)
        # email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        # 이메일 왜 안되지 ? 왜 안되지? 왜안되지 ??? 일단 유저네임으로
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            # print(email)
            print("loginsuccess")
            remember_session = request.POST.get("remember_session", False)
            if remember_session:
                settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
            return redirect("/")
        else:
            # print(email)
            print(password)
            print("nooooo")
            return render(
                request,
                "users/login.html",
                {"error": "username or password is incorrect"},
            )
    else:
        # 로그인 상태면 main으로 리다이렉트 합니다
        if request.user.is_authenticated:
            return redirect("main")
        else:
            return render(request, "auth/login.html")


# 로그아웃 뷰


def logout(request):
    auth.logout(request)
    return redirect("/")


def found(request):
    return render(request, "auth/found.html")


def found_id(request):
    return render(request, "auth/idFound.html")


def found_password(request):
    return render(request, "auth/pwFound.html")
