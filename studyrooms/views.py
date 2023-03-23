import json
import datetime
import calendar
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Studyroom, Task, Study, StudyroomInfo, Application
from users.models import User
from forum.models import Forum
from .forms import StudyroomForm, StudyForm


@login_required()
def studyroom_lobby(request):
    STUDYROOMS_PER_PAGE = 18  # 페이지당 들어갈 스터디룸 숫자
    my_studyrooms = request.user.studyroom.all().order_by("-last_update")
    studyrooms = Studyroom.objects.exclude(pk__in=my_studyrooms).order_by(
        "-last_update"
    )
    paginator = Paginator(studyrooms, STUDYROOMS_PER_PAGE)
    modified_studyrooms = paginator.get_page(request.GET.get("page", 1))
    context = {
        "myStudyrooms": my_studyrooms if modified_studyrooms.number == 1 else None,
        "studyrooms": modified_studyrooms,
        "pages": range(1, paginator.num_pages + 1),
        "currentPage": modified_studyrooms.number,
    }
    return render(request, "studyroom/lobby.html", context)


@login_required()
def create_studyroom(request):
    if request.method == "GET":
        return render(request, "studyroom/create.html")
    elif request.method == "POST":
        user = request.user
        form = StudyroomForm(request.POST)
        if form.is_valid():
            studyroom = form.save(commit=False)
            studyroom.leader = user
            studyroom.save()
            studyroom.member.add(user)
            Forum.objects.create(studyroom=studyroom, name="일반")
            return redirect("studyroom", studyroom.pk)
        else:
            return render(request, "studyroom/create.html", {"error": form.errors})


@login_required()
def studyroom(request, studyroom_id):
    user = request.user
    studyroom = get_object_or_404(Studyroom, pk=studyroom_id)
    # Studyroom Page
    if user in studyroom.member.all():
        tasks = studyroom.task_set.all()
        total_comlete_task_count = sum(
            [
                studyroomInfo.study_progress
                for studyroomInfo in StudyroomInfo.objects.filter(studyroom=studyroom)
            ]
        )
        context = {
            "studyroomId": studyroom_id,
            "studyroomName": studyroom.name,
            "memberCount": studyroom.member.count(),
            "totalStudyTime": sum(
                study.study_hours
                for study in StudyroomInfo.objects.filter(studyroom=studyroom)
            ),
            "averageProgressRate": 0
            if tasks.count() == 0
            else round(
                total_comlete_task_count
                / (tasks.count() * studyroom.member.count())
                * 100
            ),
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
        if request.method == "GET":
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
    raw_members = studyroom.member.all()
    if not user in raw_members:
        return redirect("/studyroom/" + str(studyroom_id))

    if request.method == "GET":
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
            if user == studyroom.leader:
                data = json.loads(request.body.decode())
                selected_user = User.objects.get(pk=int(data["userId"]))
                studyroom_info = selected_user.studyroom_info.get(studyroom=studyroom)
                if selected_user == studyroom.leader:
                    return JsonResponse({"message": "스터디장은 추방할 수 없습니다"})
                else:
                    # 나중에 다시 확인
                    studyroom.member.remove(selected_user)
                    return JsonResponse({"message": "추방했습니다"})
            else:
                return JsonResponse({"message": "권한이 없습니다"})
        except Exception as e:
            return JsonResponse({"message": "알 수 없는 오류가 발생했습니다"})


@login_required()
def studyroom_member_confirm(request, studyroom_id):
    user = request.user
    studyroom = get_object_or_404(Studyroom, pk=studyroom_id)
    if not user in studyroom.member.all() or user != studyroom.leader:
        return redirect("/studyroom/" + str(studyroom_id))
    if request.method == "GET":
        raw_applications = studyroom.application.all()
        applications = list()
        for application in raw_applications:
            applications.append(
                {
                    "userId": application.user.pk,
                    "username": application.user.username,
                    "content": application.content,
                }
            )
        context = {
            "studyroomId": studyroom_id,
            "isLeader": user == studyroom.leader,
            "applications": applications,
        }
        return render(request, "studyroom/studyroomMemberConfirm.html", context)
    elif request.method == "POST":
        try:
            if user == studyroom.leader:
                data = json.loads(request.body.decode())
                selected_user = User.objects.get(pk=int(data["userId"]))
                is_accepted = data["isAccepted"]
                if is_accepted:
                    studyroom.application.get(user=selected_user).delete()
                    studyroom.member.add(selected_user)
                    return JsonResponse({"message": "수락했습니다"})
                else:
                    studyroom.application.get(user=selected_user).delete()
                    return JsonResponse({"message": "거절했습니다"})
            else:
                return JsonResponse({"message": "권한이 없습니다"})
        except Exception as e:
            return JsonResponse({"message": "알수 없는 오류가 발생했습니다"})


@login_required()
def studyroom_goal(request, studyroom_id):
    user = request.user
    studyroom = get_object_or_404(Studyroom, pk=studyroom_id)
    if not user in studyroom.member.all():
        return redirect("studyroom", studyroom_id)
    if request.method == "GET":
        tasks = studyroom.task_set.all()
        my_complete_task_count = StudyroomInfo.objects.get(
            studyroom=studyroom, user=user
        ).study_progress
        total_comlete_task_count = sum(
            [
                studyroomInfo.study_progress
                for studyroomInfo in StudyroomInfo.objects.filter(studyroom=studyroom)
            ]
        )
        context = {
            "studyroomId": studyroom_id,
            "isLeader": user == studyroom.leader,
            "tasks": tasks,
            "myProgressRate": 0
            if tasks.count() == 0
            else round(my_complete_task_count / tasks.count() * 100),
            "totalProgressRate": 0
            if tasks.count() == 0
            else round(
                total_comlete_task_count
                / (tasks.count() * studyroom.member.count())
                * 100
            ),
        }
        return render(request, "studyroom/studyroomGoal.html", context)


@login_required()
def studyroom_goal_setting(request, studyroom_id):
    user = request.user
    studyroom = get_object_or_404(Studyroom, pk=studyroom_id)
    if not user in studyroom.member.all() or user != studyroom.leader:
        return redirect("studyroom", studyroom_id)

    tasks = studyroom.task_set.all()
    context = {
        "studyroomId": studyroom_id,
        "isLeader": user == studyroom.leader,
        "tasks": tasks,
    }
    if request.method == "GET":
        return render(request, "studyroom/studyroomGoalSetting.html", context)
    elif request.method == "POST":
        goal_content = request.POST.get("goal")
        if len(goal_content) == 0:
            context["error"] = "내용은 공백일 수 없습니다"
            return render(request, "studyroom/studyroomGoalSetting.html", context)

        studyroom.task_set.create(
            content=goal_content, task_number=studyroom.task_set.count() + 1
        )
        return render(request, "studyroom/studyroomGoalSetting.html", context)


@login_required()
def studyroom_calendar(request, studyroom_id):
    user = request.user
    studyroom = get_object_or_404(Studyroom, pk=studyroom_id)
    if not user in studyroom.member.all():
        return redirect("studyroom", studyroom_id)

    if request.method == "GET":
        # get PARAM에서 연/월 가져오기
        today = datetime.date.today()
        try:
            date = request.GET["date"]
            year, month = map(int, date.split("-"))
        except:
            year, month = today.year, today.month

        first_Weekday, last_day = calendar.monthrange(year, month)

        last_month = (
            str(year if month != 1 else year - 1)
            + "-"
            + str(month - 1 if month != 1 else 12)
        )
        next_month = (
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

        j = 0 if first_Weekday == 6 else first_Weekday + 1
        for i in range(last_day):
            weeks[j // 7][j % 7]["date"] = i + 1
            current_date = datetime.date(year, month, i + 1)
            weeks[j // 7][j % 7]["studyCount"] = Study.objects.filter(
                studyroom=studyroom, date=current_date
            ).count()
            weeks[j // 7][j % 7]["studyCount"] = (
                "99+"
                if weeks[j // 7][j % 7]["studyCount"] > 99
                else weeks[j // 7][j % 7]["studyCount"]
            )

            # weeks[j // 7][j % 7]["studies"] = Study.objects.filter(
            #     studyroom=studyroom, date=current_date
            # )
            if current_date <= today:
                weeks[j // 7][j % 7]["isPast"] = True
            j += 1
        # remove unused weeks
        for i in range(5, 3, -1):
            if not weeks[i][0]:
                weeks.pop()

        context = {
            "studyroomId": studyroom_id,
            "isLeader": user == studyroom.leader,
            "year": year,
            "month": month,
            "weeks": weeks,
            "lastMonth": last_month,
            "nextMonth": next_month,
        }
        return render(request, "studyroom/studyroomCalendar.html", context)


@login_required()
def studyroom_calendar_study(request, studyroom_id, year, month, day):
    user = request.user
    studyroom = get_object_or_404(Studyroom, pk=studyroom_id)
    if not user in studyroom.member.all():
        return redirect("studyroom", studyroom_id)

    # check if date is valid, if not, redirect to calendar
    try:
        selected_date = datetime.date(year, month, day)
    except ValueError:
        return redirect("studyroomCalendar", studyroom_id)

    current_progress = studyroom.studyroom_info.get(user=user).study_progress
    context = {
        "studyroomId": studyroom_id,
        "isLeader": user == studyroom.leader,
        "year": year,
        "month": month,
        "day": day,
        "tasks": studyroom.task_set.filter(
            task_number__gte=current_progress
        ),  # task_number >= current_progress
        "currentProgress": user.studyroom_info.get(studyroom=studyroom).study_progress,
        "isToday": datetime.date.today() == selected_date,
        "isFuture": datetime.date.today() < selected_date,
        "studies": Study.objects.filter(studyroom=studyroom, date=selected_date),
        "error": None,
    }
    for study in context["studies"]:
        study.progress_content = studyroom.task_set.get(
            task_number=study.progress
        ).content

    if request.method == "GET":
        return render(request, "studyroom/studyroomCalendarStudy.html", context)

    elif request.method == "POST":
        form = StudyForm(request.POST)
        if form.is_valid():
            progress_input = form.cleaned_data["progress"]
            content_input = form.cleaned_data["content"]
            learning_time_input = form.cleaned_data["learning_time"]

            # check value is valid
            if progress_input < current_progress:
                context["error"] = "진도율은 현재 진도 이상으로 설정해야 합니다"
            elif progress_input > studyroom.task_set.count():
                context["error"] = "진도율이 목표를 초과했습니다"
            elif learning_time_input <= 0:
                context["error"] = "공부 시간은 0보다 커야 합니다"
            elif learning_time_input > 24:
                context["error"] = "공부 시간은 24시간을 넘을 수 없습니다"

            if context["error"] is not None:
                return render(request, "studyroom/studyroomCalendarStudy.html", context)

            study = Study.objects.create(
                studyroom=studyroom,
                date=selected_date,
                user=user,
                learning_time=learning_time_input,
                progress=progress_input,
                content=content_input,
            )
            studyroom_info = studyroom.studyroom_info.get(user=user)
            studyroom_info.study_progress = progress_input
            studyroom_info.study_hours += learning_time_input
            studyroom_info.save()
            return redirect("studyroomCalendarStudy", studyroom_id, year, month, day)
        else:
            context["error"] = form.errors
            return render(request, "studyroom/studyroomCalendarStudy.html", context)


@login_required()
def studyroom_board(request, studyroom_id):
    user = request.user
    studyroom = get_object_or_404(Studyroom, pk=studyroom_id)
    if not user in studyroom.member.all():
        return redirect("studyroom", studyroom_id)
    if user in studyroom.member.all():
        forum = Forum.objects.filter(studyroom=studyroom)[0]
        return redirect("forum", forum.pk)
