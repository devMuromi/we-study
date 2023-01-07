from django.urls import path, include
from . import views
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path("make/", views.studyroomMake, name="studyroomMake"),
    path("my/", views.studyroomMy, name="studyroomMy"),
    path("join/", views.studyroomJoin, name="studyroomJoin"),
    path("room/<int:room_id>", views.studyroom, name="studyroom"),
    path("room/<int:room_id>/board", views.studyroomBoard, name="studyroomBoard"),
    path(
        "room/<int:room_id>/calendar", views.studyroomCalendar, name="studyroomCalendar"
    ),
    path(
        "room/<int:room_id>/calendar/<int:year>-<int:month>-<int:day>",
        views.studyroomTask,
        name="studyroomTask",
    ),
    path("room/<int:room_id>/member", views.studyroomMember, name="studyroomMember"),
    path("room/<int:room_id>/time", views.studyroomTime, name="studyroomTime"),
    path(
        "room/<int:room_id>/progress", views.studyroomProgress, name="studyroomProgress"
    ),
    path("room/<int:room_id>/manage", views.studyroomManage, name="studyroomManage"),
    path("room/<int:room_id>/confirm", views.studyroomConfirm, name="studyroomConfirm"),
    path("room/<int:room_id>/goal", views.studyroomGoal, name="studyroomGoal"),
]
