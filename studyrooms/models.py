from django.db import models
from users.models import User
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver


class Studyroom(models.Model):
    leader = models.ForeignKey(
        User, related_name="my_studyroom", on_delete=models.CASCADE
    )
    member = models.ManyToManyField(
        User, related_name="studyroom", through="StudyroomInfo"
    )
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=64)
    created_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    studyroom = models.ForeignKey(Studyroom, on_delete=models.CASCADE)
    task_number = models.PositiveIntegerField()
    content = models.TextField()


class Study(models.Model):
    studyroom = models.ForeignKey(Studyroom, on_delete=models.CASCADE)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField(null=True)
    learning_time = models.PositiveIntegerField()
    progress = models.IntegerField()

    class Meta:
        verbose_name = "study"
        verbose_name_plural = "studies"


# 유저당 스터디룸에 하나씩 생기는 기록 모델. m2m_changed signal이 적용
class StudyroomInfo(models.Model):
    studyroom = models.ForeignKey(
        Studyroom, on_delete=models.CASCADE, related_name="studyroom_info"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="studyroom_info"
    )
    study_hours = models.IntegerField(default=0)
    study_progress = models.IntegerField(default=0)


class Application(models.Model):
    studyroom = models.ForeignKey(
        Studyroom, on_delete=models.CASCADE, related_name="application"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="application")
    content = models.TextField()


# @receiver(m2m_changed, sender=Studyroom.member.through)
# def my_callback(sender, **kwargs):
#     if kwargs["reverse"] == False:
#         studyroom = kwargs["instance"]
#         user = User.objects.get(id=list(kwargs["pk_set"])[0])
#     elif kwargs["reverse"] == True:
#         studyroom = Studyroom.objects.get(id=list(kwargs["pk_set"])[0])
#         user = kwargs["instance"]

#     if kwargs["action"] == "pre_add":
#         StudyroomInfo.objects.create(user=user, studyroom=studyroom)
#     elif kwargs["action"] == "pre_remove":
#         StudyroomInfo.objects.get(user=user, studyroom=studyroom).delete()
