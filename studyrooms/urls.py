from django.urls import path
from . import views

urlpatterns = [
    path("lobby/", views.studyroom_lobby, name="studyroomLobby"),
    path("create/", views.create_studyroom, name="createStudyroom"),
    path("<int:studyroom_id>", views.studyroom, name="studyroom"),
    path("<int:studyroom_id>/member", views.studyroom_member, name="studyroomMember"),
    path(
        "<int:studyroom_id>/confirm",
        views.studyroom_member_confirm,
        name="studyroomMemberConfirm",
    ),
    path(
        "<int:studyroom_id>/progress",
        views.studyroom_goal,
        name="studyroomProgress",
    ),
    path(
        "<int:studyroom_id>/goal",
        views.studyroom_goal_setting,
        name="studyroomGoal",
    ),
    path(
        "<int:studyroom_id>/calendar",
        views.studyroom_calendar,
        name="studyroomCalendar",
    ),
    path(
        "<int:studyroom_id>/calendar/<int:year>-<int:month>-<int:day>",
        views.studyroom_calendar_study,
        name="studyroomCalendarStudy",
    ),
    path("<int:studyroom_id>/board", views.studyroom_board, name="studyroomBoard"),
    # path(
    #     "<int:studyroom_id>/manage-request", views.studyroomConfirm, name="studyroomConfirm"
    # ),
]
