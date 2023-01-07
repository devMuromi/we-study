from django.db import models
from studyrooms.models import *
from users.models import *


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    THEMA_CHOICES = (
        ("n", "공지게시판"),
        ("f", "자유게시판"),
        ("q", "질문게시판"),
        ("i", "정보게시판"),
    )
    thema = models.CharField(
        max_length=1, choices=THEMA_CHOICES
    )  # 자유게시판/ 질문게시판/ 정보게시판 이런거...
    author = models.ForeignKey("users.user", on_delete=models.CASCADE)
    studyroom = models.ForeignKey("studyrooms.Studyroom", on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Comment(models.Model):
    author = models.ForeignKey("users.User", on_delete=models.CASCADE)
    content = models.TextField()
    board = models.ForeignKey("Post", on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
