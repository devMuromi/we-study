from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import auth
from studyrooms.models import *
from django.contrib.auth.decorators import login_required
from .forms import ChangePasswordForm


def main(request):
    return render(request, "main/main.html")


@login_required()
def my_page(request):
    user = request.user
    context = {
        "name": request.user.username,
        "email": request.user.email,
        "studyroom_number": str(request.user.studyroom.count()),
        "study_time": sum(
            study.study_hours for study in StudyroomInfo.objects.filter(user=user)
        ),
    }
    return render(request, "mypage/myPage.html", context)


@login_required()
def my_info(request):
    context = {
        "name": request.user.username,
        "email": request.user.email,
        "job": request.user.get_job_display,
    }
    return render(request, "mypage/myInfo.html", context)


@login_required()
def my_password(request):
    context = {}
    if request.method == "GET":
        return render(request, "mypage/mypassword.html", context)
    elif request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if not form.is_valid():
            context["error"] = "새 비밀번호 반복이 다릅니다"
            return render(request, "mypage/myPassword.html", context)
        else:
            user = request.user
            old_password = form.cleaned_data["old_password"]
            new_password = form.cleaned_data["new_password"]

            if not check_password(old_password, user.password):
                context["error"] = "비밀번호가 틀렸습니다"
                return render(request, "mypage/myPassword.html", context)
            else:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                return redirect("login")
