from django.db import models
from studyrooms.models import Studyroom
from users.models import User


class Forum(models.Model):
    name = models.CharField(max_length=32)
    studyroom = models.ForeignKey(Studyroom, on_delete=models.PROTECT)


class Thread(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.PROTECT)
    title = models.CharField(max_length=200)
    create_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    upvote = models.PositiveIntegerField(default=0)
    downvote = models.PositiveIntegerField(default=0)
    isDeleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    isAnonymous = models.BooleanField(default=False)
    isDeleted = models.BooleanField(default=False)

    def __str__(self):
        return self.content[:10]
