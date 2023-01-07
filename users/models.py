from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from studyrooms.models import *


class User(AbstractUser):
    JOB_CHOICES = (
        ("S", "학생"),
        ("T", "교사"),
        {"O", "기타"},
    )
    email = models.EmailField(max_length=254)
    job = models.CharField(max_length=2, choices=JOB_CHOICES)
    profile_picture = models.ImageField(
        blank=True,
        upload_to="user/image/%Y/%m/%d",
        height_field=None,
        width_field=None,
        max_length=None,
    )
    study_room = models.ManyToManyField("studyrooms.Studyroom", related_name="member")


@receiver(m2m_changed, sender=User.study_room.through)
def my_callback(sender, **kwargs):
    if kwargs["reverse"] == True:
        studyroom = kwargs["instance"]
        user = User.objects.get(id=list(kwargs["pk_set"])[0])
    else:
        studyroom = Studyroom.objects.get(id=list(kwargs["pk_set"])[0])
        user = kwargs["instance"]

    if kwargs["action"] == "pre_add":
        print("pre_add")
        Progress_rate.objects.create(user=user, studyroom=studyroom)
    elif kwargs["action"] == "pre_remove":
        print("pre_remove")
        Progress_rate.objects.get(user=user, studyroom=studyroom).delete()
