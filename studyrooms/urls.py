from django.urls import path, include
from . import views

urlpatterns = [
    path("make/", views.studyroom_create, name="studyroomMake"),
    path("lobby/", views.studyroomJoin, name="studyroomJoin"),
    path("room/<int:room_id>", views.studyroom, name="studyroom"),
    path("room/<int:room_id>/board", views.studyroom_board, name="studyroomBoard"),
    path(
        "room/<int:room_id>/calendar",
        views.studyroom_calendar,
        name="studyroomCalendar",
    ),
    path(
        "room/<int:room_id>/calendar/<int:year>-<int:month>-<int:day>",
        views.studyroom_task,
        name="studyroomTask",
    ),
    path("room/<int:room_id>/member", views.studyroom_member, name="studyroomMember"),
    path(
        "room/<int:room_id>/progress",
        views.studyroom_progress,
        name="studyroomProgress",
    ),
    path("room/<int:room_id>/manage", views.studyroomManage, name="studyroomManage"),
    path("room/<int:room_id>/confirm", views.studyroomConfirm, name="studyroomConfirm"),
    path("room/<int:room_id>/goal", views.studyroomGoal, name="studyroomGoal"),
]
