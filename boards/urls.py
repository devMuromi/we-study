from django.urls import path, include
from . import views
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path("board/<str:board_id>/<int:studyroom_id>", views.board, name="board"),
    path("new/<int:room_id>/<str:board_thema>", views.postnew, name="postnew"),
    path("study/<str:board_thema>/<int:room_id>", views.postcreate, name="postcreate"),
    path("detail/<int:room_id>/<int:post_id>", views.detail, name="detail"),
    path("postdelete/<int:room_id>/<int:post_id>", views.postdelete, name="postdelete"),
    path("postedit/<int:room_id>/<int:post_id>", views.postedit, name="postedit"),
    path("postupdate/<int:room_id>/<int:post_id>", views.postupdate, name="postupdate"),
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
