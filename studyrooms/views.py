import json
import datetime
import calendar
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Studyroom, Task, Schedule, Study, StudyroomInfo, Application
from users.models import User
from .forms import StudyroomForm, StudyForm


@login_required()
def studyroom_lobby(request):
    STUDYROOMS_PER_PAGE = 18  # 페이지당 들어갈 스터디룸 숫자
    my_studyrooms = request.user.studyroom.all().order_by("-last_update")
    studyrooms = Studyroom.objects.all().order_by("-last_update")
    for studyroom in studyrooms:
        if studyroom in my_studyrooms:
            studyrooms = studyrooms.exclude(pk=studyroom.pk)
    # studyrooms = my_studyrooms.union(studyrooms)
    # print(studyrooms)

    paginator = Paginator(studyrooms, STUDYROOMS_PER_PAGE)
    page = request.GET.get("page")
    modified_studyrooms = paginator.get_page(page)
    pages = range(1, paginator.num_pages + 1)

    context = {
        "myStudyrooms": None,
        "studyrooms": modified_studyrooms,
        "pages": pages,
        "currentPage": 1 if page == None else int(page),
    }
    if page == None or page == "1":
        context["myStudyrooms"] = my_studyrooms
    return render(request, "studyroom/lobby.html", context)


@login_required()
def create_studyroom(request):
    if request.method == "GET":
        return render(request, "studyrooms/create.html")
    elif request.method == "POST":
        user = request.user
        form = StudyroomForm(request.POST)
        if form.is_valid():
            studyroom = Studyroom.objects.create(**form.cleaned_data, leader=user)
            studyroom.member.add(user)
            return redirect("studyroom", studyroom.pk)
        else:
            return render(request, "studyroom/create.html", {"error": form.errors})


@login_required()
def studyroom(request, studyroom_id):
    user = request.user
    studyroom = get_object_or_404(Studyroom, pk=studyroom_id)
    # Studyroom Page
    if user in studyroom.member.all():
        context = {
            "studyroomId": studyroom_id,
            "name": studyroom.name,
            "memberCount": studyroom.member.count(),
            "totalStudyTime": 0,
            "averageProgressRate": 0,
            "isLeader": user == studyroom.leader,
        }
        return render(request, "studyroom/studyroom.html", context)
    # Application Page
    else:
        context = {
            "name": studyroom.name,
            "description": studyroom.description,
            "leader": studyroom.leader.username,
            "memberCount": studyroom.member.count(),
        }
        if studyroom.application.filter(user=user).count() > 0:
            context["error"] = "이미 해당 스터디룸에 참여 신청을 했습니다"
            return render(request, "studyroom/request.html", context)
        elif request.method == "GET":
            return render(request, "studyroom/request.html", context)
        elif request.method == "POST":
            Application.objects.create(
                user=user, studyroom=studyroom, content=request.POST["application"]
            )
            return redirect("studyroomLobby")


@login_required()
def studyroom_member(request, studyroom_id):
    user = request.user
    studyroom = get_object_or_404(Studyroom, pk=studyroom_id)
    if not user in studyroom.member.all():
        return redirect("/studyroom/" + str(studyroom_id))

    raw_members = studyroom.member.all()
    members = list()
    for member in raw_members:
        members.append(
            {
                "id": member.pk,
                "username": member.username,
                "isLeader": member == studyroom.leader,
                "studyHours": member.studyroom_info.get(
                    studyroom=studyroom
                ).study_hours,
                "studyProgress": member.studyroom_info.get(
                    studyroom=studyroom
                ).study_progress,
            }
        )
    if request.method == "GET":
        context = {
            "studyroomId": studyroom_id,
            "name": studyroom.name,
            "description": studyroom.description,
            "leader": studyroom.leader.username,
            "isLeader": user == studyroom.leader,
            "members": members,
        }
        return render(request, "studyroom/studyroomMember.html", context)
    elif request.method == "POST":
        try:
            data = json.loads(request.body.decode())
            print(data, type(data))
            selected_user = User.objects.get(pk=int(data["userId"]))
            studyroom_info = selected_user.studyroom_info.get(studyroom=studyroom)
            if selected_user == studyroom.leader:
                return JsonResponse({"message": "스터디장은 추방할 수 없습니다"})
            else:
                # studyroom.member.remove(selected_user)
                # studyroom_info.delete()
                return JsonResponse({"message": "success"})
        except Exception as e:
            print(e)
            return JsonResponse({"message": "알수 없는 오류가 발생했습니다"})


# def studyroomConfirm(request, room_id):

#         if studyroom.leader == user:
#             if request.method == "POST":
#                 data = json.loads(request.body.decode())
#                 application = Application.objects.get(pk=int(data["appId"]))
#                 if data["choice"] == "accept":
#                     application.userId.study_room.add(studyroom)
#                     application.delete()

#                 elif data["choice"] == "decline":
#                     # 추후에 신청 거절/수락 여부를 알림등으로 알리는 기능 추가
#                     application.delete()

#                 return HttpResponse("잘못된 접근")
#             else:
#                 applications = studyroom.application.all()
#                 context = {
#                     "room_id": room_id,
#                     "isCaptain": True,
#                     "applications": applications,
#                 }
#                 return render(request, "studyrooms/studyroomConfirm.html", context)
#         # 스터디원 검증
#         elif user in studyroom.member.all():
#             context["isCaptain"] = False
#             return render(request, "studyrooms/studyroomConfirm.html", context)
#         else:
#             return redirect("studyroom", room_id)
#     else:
#         return redirect("login")


def studyroom_task(request, room_id, year, month, day):
    if request.user.is_authenticated:
        context = {
            "room_id": room_id,
        }
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)

        if user in studyroom.member.all():
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


def studyroom_calendar(request, room_id):
    if request.user.is_authenticated:
        context = {
            "room_id": room_id,
        }
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)

        if user in studyroom.member.all():
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
                "isLeader": user == studyroom.leader,
            }
            return render(request, "studyrooms/studyroomCalendar.html", context)
        else:
            return redirect("studyroom", room_id)
    else:
        return redirect("login")


def studyroom_board(request, room_id):
    if request.user.is_authenticated:
        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)
        if user in studyroom.member.all():
            return redirect("board", "N", room_id)
        else:
            return redirect("studyroom", room_id)
    else:
        return redirect("login")


def studyroom_progress(request, room_id):
    if request.user.is_authenticated:

        user = request.user
        studyroom = get_object_or_404(Studyroom, pk=room_id)

        if user in studyroom.member.all():
            tasks = studyroom.progress_task_set.all()
            jobs = studyroom.progress_rate_set.all()

            total_progress_rate = (
                0
                if len(tasks or jobs) == 0
                else round(
                    sum([job.totalProgress for job in jobs])
                    / len(tasks)
                    / studyroom.member.count()
                    * 100
                )
            )
            my_progress_rate = round(
                studyroom.progress_rate_set.get(user=user).totalProgress
                / len(tasks)
                * 100
            )
            context = {
                "room_id": room_id,
                "totalProgressRate": total_progress_rate,
                "myProgressRate": my_progress_rate,
                "tasks": tasks,
                "isLeader": user == studyroom.leader,
            }
            return render(request, "studyrooms/studyroomProgress.html", context)
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
        elif user in studyroom.member.all():
            context["isCaptain"] = False
            return render(request, "studyrooms/studyroomGoal.html", context)
        else:
            return redirect("studyroom", room_id)
    else:
        return redirect("login")
