from django.urls import path, include
from . import views
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path("<int:studyroom_id>/<str:forum_type>/", views.forum, name="board"),
    path("post/<int:studyroom_id>/<int:post_id>", views.post, name="detail"),
    path(
        "create/<int:studyroom_id>/<str:forum_type>/",
        views.create_post,
        name="craetePost",
    ),
    path("edit/<int:studyroom_id>/<int:post_id>", views.edit_post, name="postedit"),
    path(
        "delete/<int:studyroom_id>/<int:post_id>", views.delete_post, name="postdelete"
    ),
    path(
        "update/<int:studyroom_id>/<int:post_id>", views.update_post, name="postupdate"
    ),
    path(
        "postsearch/<int:room_id>/<str:board_thema>",
        views.postsearch,
        name="postsearch",
    ),
    path(
        "commentdelete/<int:room_id>/<int:post_id>/<int:comment_id>",
        views.commentdelete,
        name="commentdelete",
    ),
]
