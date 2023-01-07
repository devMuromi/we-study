from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.studyroom_create, name="studyroomMake"),
    path("lobby/", views.studyroom_lobby, name="studyroomJoin"),
    path("<int:room_id>", views.studyroom, name="studyroom"),
    path("<int:room_id>/board", views.studyroom_board, name="studyroomBoard"),
    path(
        "<int:room_id>/calendar",
        views.studyroom_calendar,
        name="studyroomCalendar",
    ),
    path(
        "<int:room_id>/calendar/<int:year>-<int:month>-<int:day>",
        views.studyroom_task,
        name="studyroomTask",
    ),
    path("<int:room_id>/member", views.studyroom_member, name="studyroomMember"),
    path(
        "<int:room_id>/progress",
        views.studyroom_progress,
        name="studyroomProgress",
    ),
    path("<int:room_id>/manage", views.studyroomManage, name="studyroomManage"),
    path(
        "<int:room_id>/manage-request", views.studyroomConfirm, name="studyroomConfirm"
    ),
    path("<int:room_id>/manage-task", views.studyroomGoal, name="studyroomGoal"),
]
