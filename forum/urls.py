from django.urls import path, include
from . import views
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path("<int:forum_id>/", views.forum, name="forum"),
    path(
        "thread/<int:forum_id>/create/",
        views.create_thread,
        name="createThread",
    ),
    path(
        "thread/<int:thread_id>/",
        views.thread,
        name="thread",
    ),
    path("thread/<int:thread_id>/delete/", views.delete_thread, name="deleteThread"),
    path(
        "thread/<int:thread_id>/<int:post_id>",
        views.delete_post,
        name="deltePost",
    ),
]
