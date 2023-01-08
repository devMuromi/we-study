from django.shortcuts import render, redirect
from .models import User
from django.contrib import auth
from .forms import UserForm
from django.conf import settings


def sign_up(request):
    def get_job_choice():
        job_choices = []
        for job_choice in User.JOB_CHOICES:
            job_choices.append({"value": job_choice[0], "name": job_choice[1]})
        return job_choices

    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("main")
        else:
            form = UserForm()
            return render(request, "auth/signup.html", {"jobChoice": get_job_choice()})
    elif request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            auth.login(request, user)
            return redirect("/")
        else:
            context = {
                "jobChoice": get_job_choice(),
                "error": "회원가입에 실패했습니다",
            }
            return render(request, "auth/signup.html", context)


def login(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("main")
        else:
            return render(request, "auth/login.html")
    elif request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            if request.POST.get("remember_session", False):
                settings.SESSION_EXPIRE_AT_BROWSER_CLOSE = False
            return redirect(request.GET.get("next", "/"))
        else:
            return render(
                request,
                "auth/login.html",
                {"error": "아이디 또는 비밀번호가 틀렸습니다"},
            )


def logout(request):
    auth.logout(request)
    return redirect("/")


# def found(request):
#     return render(request, "auth/found.html")


# def found_id(request):
#     return render(request, "auth/idFound.html")


# def found_password(request):
#     return render(request, "auth/pwFound.html")
