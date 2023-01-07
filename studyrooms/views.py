from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from users.models import *
from applications.models import *
from django.contrib import auth
from django.core.paginator import Paginator
from .forms import StudyroomForm, TodoForm
from applications.models import *
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json
import datetime
import calendar


def studyroom(request, room_id):
    if request.user.is_authenticated:
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)

        # 스터디룸 페이지
        if user in studyroom.users.all():
            taskCount = studyroom.progress_task_set.count()
            averageProgressRate = (
                0
                if taskCount == 0
                else round(
                    sum(
                        [
                            progressRate.totalProgress
                            for progressRate in studyroom.progress_rate_set.all()
                        ]
                    )
                    / taskCount
                    * 100,
                    1,
                )
            )
            context = {
                "room_id": room_id,
                "memberCount": studyroom.users.count(),
                "studyroomName": studyroom.studyroom_name,
                "totalStudyTime": sum(
                    [
                        progressRate.totalHour
                        for progressRate in studyroom.progress_rate_set.all()
                    ]
                ),
                "averageProgressRate": averageProgressRate,
            }
            return render(request, "studyrooms/studyroom.html", context)
        # 신청서 페이지
        else:
            context = {
                "studyName": studyroom.studyroom_name,
                "studyCaptain": studyroom.leader.username,
                "studyField": studyroom.studyroom_classification,
                "studyParticipants": studyroom.users.count(),
                "studyOpen": "공개범위가 이곳에 들어갑니다",
            }
            if request.method == "POST":
                studyroom = get_object_or_404(Studyroom, pk=room_id)
                if studyroom.application.filter(userId=request.user).count() == 0:
                    application = Application()
                    application.userId = request.user
                    application.studyroomId = studyroom
                    application.text = request.POST["studyroom_classification"]
                    application.save()
                else:
                    context["error"] = "이미 스터디룸 참여 요청을 보냈습니다"
                    return render(request, "studyrooms/request.html", context)
                return redirect("main")
            else:
                return render(request, "studyrooms/request.html", context)
    else:
        return redirect("login")


def studyroomCalendar(request, room_id):
    if request.user.is_authenticated:
        context = {
            "room_id": room_id,
        }
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)

        if user in studyroom.users.all():
            today = datetime.date.today()
            todayMonth = today.month
            todayYear = today.year

            # get PARAM에서 연/월 가져오기
            try:
                date = request.GET["date"]
                year, month = map(int, date.split("-"))
            except:
                year, month = todayYear, todayMonth

            startWeekday, lastDay = calendar.monthrange(year, month)

            lastMonth = (
                str(year if month != 1 else year - 1)
                + "-"
                + str(month - 1 if month != 1 else 12)
            )
            nextMonth = (
                str(year if month != 12 else year + 1)
                + "-"
                + str(month + 1 if month != 12 else 1)
            )

            weeks = [
                [{}, {}, {}, {}, {}, {}, {}],
                [{}, {}, {}, {}, {}, {}, {}],
                [{}, {}, {}, {}, {}, {}, {}],
                [{}, {}, {}, {}, {}, {}, {}],
                [{}, {}, {}, {}, {}, {}, {}],
                [{}, {}, {}, {}, {}, {}, {}],
            ]

            j = startWeekday + 1
            for i in range(lastDay):
                weeks[j // 7][j % 7]["day"] = i + 1
                selectedDate = datetime.date(year, month, i + 1)
                dayCalendar, isCalendarCreated = Calendar.objects.get_or_create(
                    studyroom=studyroom, date=selectedDate
                )

                todos = dayCalendar.todo_set.all()
                todoList = [todo.writer for todo in todos]
                weeks[j // 7][j % 7]["tasks"] = todoList

                j += 1

            context = {
                "room_id": room_id,
                "weeks": weeks,
                "year": year,
                "month": month,
                "lastMonth": lastMonth,
                "nextMonth": nextMonth,
            }
            return render(request, "studyrooms/studyroomCalendar.html", context)
        else:
            return redirect("studyroom", room_id)
    else:
        return redirect("login")


def studyroomTask(request, room_id, year, month, day):
    if request.user.is_authenticated:
        context = {
            "room_id": room_id,
        }
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)

        if user in studyroom.users.all():
            if request.method == "POST":
                form = TodoForm(request.POST)
                if form.is_valid():
                    currentUserTask = studyroom.progress_rate_set.get(
                        user=user
                    ).totalProgress
                    # 정상적이지 않은 접근으로 progress값이 범위 밖일때
                    if (
                        form.cleaned_data["progress"] < currentUserTask
                        or form.cleaned_data["progress"]
                        > studyroom.progress_task_set.count()
                    ):
                        context["error_message"] = "진도율이 잘못되었습니다, 새로 고침을 해주세요"
                        return render(request, "studyrooms/studyroomTask.html", context)

                    selectedDate = datetime.date(year, month, day)
                    calendar, isCalendarCreated = Calendar.objects.get_or_create(
                        studyroom=studyroom, date=selectedDate
                    )

                    todo = Todo()
                    todo.calendar = calendar
                    todo.writer = user
                    todo.content = form.cleaned_data["content"]
                    todo.learning_time = form.cleaned_data["learning_time"]
                    todo.progress = form.cleaned_data["progress"]
                    todo.save()

                    progress_rate = studyroom.progress_rate_set.get(user=user)
                    progress_rate.totalHour = (
                        progress_rate.totalHour + todo.learning_time
                    )
                    progress_rate.totalProgress = todo.progress
                    progress_rate.save()
                    return redirect("studyroomTask", room_id, year, month, day)
                else:
                    error = form.errors
                    context["error_message"] = error
                    return render(request, "studyrooms/studyroomTask.html", context)

            else:
                try:
                    changMonthToEng = {
                        1: "Jan",
                        2: "Feb",
                        3: "Mar",
                        4: "Apr",
                        5: "May",
                        6: "Jun",
                        7: "Jul",
                        8: "Aug",
                        9: "Sep",
                        10: "Oct",
                        11: "Nov",
                        12: "Dec",
                    }
                    selectedDate = datetime.date(year, month, day)
                    context["year"] = year
                    context["month"] = month
                    context["month_eng"] = changMonthToEng[month]
                    context["day"] = day

                    # todo 목록
                    calendar, isCalendarCreated = Calendar.objects.get_or_create(
                        studyroom=studyroom, date=selectedDate
                    )
                    context["todos"] = calendar.todo_set.all()
                    for todo in context["todos"]:
                        todo.progress = studyroom.progress_task_set.get(
                            taskNumber=todo.progress
                        ).task

                    tasks = studyroom.progress_task_set.all()
                    currentUserTask = studyroom.progress_rate_set.get(
                        user=user
                    ).totalProgress
                    context["tasks"] = tasks[
                        (currentUserTask - 1 if currentUserTask > 0 else 0) :
                    ]

                except ValueError:
                    context["error_message"] = "날짜가 잘못되었습니다"
                return render(request, "studyrooms/studyroomTask.html", context)
        else:
            return redirect("studyroom", room_id)
    else:
        return redirect("login")


def studyroomBoard(request, room_id):
    if request.user.is_authenticated:
        context = {
            "room_id": room_id,
        }
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)

        if user in studyroom.users.all():
            return redirect("board", "n", room_id)
        else:
            return redirect("studyroom", room_id)
    else:
        return redirect("login")


def studyroomMember(request, room_id):
    if request.user.is_authenticated:
        context = {
            "room_id": room_id,
        }
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)

        if user in studyroom.users.all():
            context["users"] = studyroom.users.all()
            return render(request, "studyrooms/studyroomMember.html", context)
        else:
            return redirect("studyroom", room_id)
    else:
        return redirect("login")


def studyroomTime(request, room_id):
    if request.user.is_authenticated:
        context = {
            "room_id": room_id,
        }
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)

        if user in studyroom.users.all():
            studyCount = 0
            calendars = studyroom.calendar_set.all()
            for calendar in calendars:
                studyCount += calendar.todo_set.filter(writer=user).count()
            context["study_count"] = studyCount
            context["study_time"] = (
                studyroom.progress_rate_set.all().get(user=user).totalHour
            )
            return render(request, "studyrooms/studyroomTime.html", context)
        else:
            return redirect("studyroom", room_id)
    else:
        return redirect("login")


def studyroomProgress(request, room_id):
    if request.user.is_authenticated:
        context = {
            "room_id": room_id,
        }
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)

        if user in studyroom.users.all():
            context["tasks"] = studyroom.progress_task_set.all()
            return render(request, "studyrooms/studyroomProgress.html", context)
        else:
            return redirect("studyroom", room_id)
    else:
        return redirect("login")


def studyroomConfirm(request, room_id):
    if request.user.is_authenticated:
        context = {
            "room_id": room_id,
        }
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)

        # 스터디장 검증
        if studyroom.leader == user:
            if request.method == "POST":
                data = json.loads(request.body.decode())
                application = Application.objects.get(pk=int(data["appId"]))
                if data["choice"] == "accept":
                    application.userId.study_room.add(studyroom)
                    application.delete()

                elif data["choice"] == "decline":
                    # 추후에 신청 거절/수락 여부를 알림등으로 알리는 기능 추가
                    application.delete()

                return HttpResponse("잘못된 접근")
            else:
                applications = studyroom.application.all()
                context = {
                    "room_id": room_id,
                    "isCaptain": True,
                    "applications": applications,
                }
                return render(request, "studyrooms/studyroomConfirm.html", context)
        # 스터디원 검증
        elif user in studyroom.users.all():
            context["isCaptain"] = False
            return render(request, "studyrooms/studyroomConfirm.html", context)
        else:
            return redirect("studyroom", room_id)
    else:
        return redirect("login")


# 이후에 스터디장 이전 기능 추가하기


def studyroomManage(request, room_id):
    if request.user.is_authenticated:
        context = {
            "room_id": room_id,
        }
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)

        # 스터디장 검증
        if studyroom.leader == request.user:
            if request.method == "POST":
                data = json.loads(request.body.decode())
                selectedUser = User.objects.get(pk=int(data["userId"]))
                if data["choice"] == "ban":
                    if selectedUser == studyroom.leader:
                        # js로 처리해서 작동안함. 이후에 ajax로 경고할 수 있는지 확인
                        context = {
                            "room_id": room_id,
                            "isCaptain": True,
                            "users": studyroom.users.all(),
                            "error_message": "스터디장은 추방할 수 없습니다",
                        }
                        return render(
                            request, "studyrooms/studyroomManage.html", context
                        )
                    else:
                        selecedUser.study_room.remove(studyroom)

                        return HttpResponse("잘못된 접근")
            else:
                context = {
                    "room_id": room_id,
                    "isCaptain": True,
                    "users": studyroom.users.all(),
                }
                return render(request, "studyrooms/studyroomManage.html", context)
        # 스터디원 검증
        elif user in studyroom.users.all():
            context["isCaptain"] = False
            return render(request, "studyrooms/studyroomManage.html", context)
        else:
            return redirect("studyroom", room_id)
    else:
        return redirect("login")


def studyroomGoal(request, room_id):
    if request.user.is_authenticated:
        context = {
            "room_id": room_id,
        }
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)
        # 스터디장 검증
        if studyroom.leader == user:
            context = {
                "room_id": room_id,
                "isCaptain": True,
                "tasks": studyroom.progress_task_set.all(),
            }
            if request.method == "POST":
                goalContent = request.POST.get("textarea-goal")
                if len(goalContent) == 0:
                    context.update({"error_message": "내용은 공백일 수 없습니다"})
                    return render(request, "studyrooms/studyroomGoal.html", context)

                studyroom.progress_task_set.create(
                    task=goalContent, taskNumber=studyroom.progress_task_set.count() + 1
                )
                return render(request, "studyrooms/studyroomGoal.html", context)
            else:
                return render(request, "studyrooms/studyroomGoal.html", context)
        # 스터디원 검증
        elif user in studyroom.users.all():
            context["isCaptain"] = False
            return render(request, "studyrooms/studyroomGoal.html", context)
        else:
            return redirect("studyroom", room_id)
    else:
        return redirect("login")


def studyroomMake(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = StudyroomForm(request.POST)
            if form.is_valid():
                studyroom = Studyroom()
                studyroom.studyroom_name = form.cleaned_data["studyroom_name"]
                studyroom.studyroom_classification = form.cleaned_data[
                    "studyroom_classification"
                ]
                studyroom.leader = request.user
                studyroom.save()
                studyroom.users.add(request.user)
                return redirect("studyroom", studyroom.pk)
            else:
                error = form.errors
                context = {"error_message": error}
                return render(request, "studyrooms/make.html", context)
        else:
            return render(request, "studyrooms/make.html")
    else:
        return redirect("login")


def studyroomJoin(request):
    STUDYROOMSPERPAGE = 20  # 페이지당 들어갈 스터디룸 숫자
    if request.user.is_authenticated:
        my_studyrooms = request.user.study_room.all()

        studyrooms = Studyroom.objects.all().order_by("-pk")
        for studyroom in studyrooms:
            if studyroom in my_studyrooms:
                studyrooms = studyrooms.exclude(pk=studyroom.pk)

        paginator = Paginator(studyrooms, STUDYROOMSPERPAGE)
        page = request.GET.get("page")
        modified_studyrooms = paginator.get_page(page)
        pages = range(1, paginator.num_pages + 1)

        context = {
            "myStudyrooms": None,
            "studyrooms": modified_studyrooms,
            "pages": pages,
        }
        if page == None or page == "1":
            context["myStudyrooms"] = my_studyrooms

        return render(request, "studyrooms/join.html", context)
    else:
        return redirect("login")
