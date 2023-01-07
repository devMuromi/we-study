from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.hashers import check_password
from django.contrib import auth
from studyrooms.models import *


def main(request):
    return render(request, "main/main.html")


def myPage(request):
    if request.user.is_authenticated:
        studyrooms = request.user.study_room.all()
        studyTime = 0
        for studyroom in studyrooms:
            progressRate = Progress_rate.objects.get(
                user=request.user, studyroom=studyroom
            )
            studyTime += progressRate.totalHour
        context = {
            "name": request.user.username,
            "email": request.user.email,
            "studyroom_number": str(request.user.study_room.count()),
            "study_time": studyTime,
        }
        return render(request, "mypage/mypage.html", context)
    else:
        return redirect("login")


def myInfo(request):
    if request.user.is_authenticated:
        gender = "other"
        if request.user.gender == "f":
            gender = "female"
        elif request.user.gender == "m":
            gender = "male"
        context = {
            "name": request.user.username,
            "email": request.user.email,
            "gender": gender,
            "birthDate": request.user.birth_date,
        }
        return render(request, "mypage/myinfo.html", context)
    else:
        return redirect("login")


def myCalender(request):
    if request.user.is_authenticated:
        context = {"test": "test"}
        return render(request, "mypage/mycalender.html", context)
    else:
        return redirect("login")


def myPassword(request):
    context = {}
    if request.user.is_authenticated:
        if request.method == "POST":
            current_password = request.POST.get("current_password")
            user = request.user
            if check_password(current_password, user.password):
                new_password = request.POST.get("new_password")
                new_password2 = request.POST.get("new_password2")
                if new_password == new_password2:
                    if len(new_password) > 0:
                        user.set_password(new_password)
                        user.save()
                        auth.login(request, user)
                        return redirect("main")
                    else:
                        context.update({"error_message": "비밀번호는 공백으로 설정할 수 없습니다"})
                        return render(request, "mypage/mypassword.html", context)
                else:
                    context.update({"error_message": "새 비밀번호가 일치하지 않습니다"})
                    return render(request, "mypage/mypassword.html", context)
            else:
                context.update({"error_message": "현재 비밀번호가 정확하지 않습니다"})
                return render(request, "mypage/mypassword.html", context)
        else:
            return render(request, "mypage/mypassword.html", context)
    else:
        return redirect("login")
