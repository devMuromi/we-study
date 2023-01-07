from django.db import models
from studyrooms.models import Studyroom
from users.models import User


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    FORUM_CHOICES = (
        ("N", "공지게시판"),
        ("G", "자유게시판"),
        ("Q", "질문게시판"),
        ("I", "정보게시판"),
    )
    type = models.CharField(max_length=1, choices=FORUM_CHOICES)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    studyroom = models.ForeignKey(Studyroom, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
