from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    JOB_CHOICES = (
        ("S", "학생"),
        ("T", "교사"),
        ("O", "기타"),
    )
    email = models.EmailField(max_length=254)
    job = models.CharField(max_length=4, choices=JOB_CHOICES)
    profile_picture = models.ImageField(
        blank=True,
        upload_to="user/image/%Y/%m/%d",
        height_field=None,
        width_field=None,
        max_length=None,
    )
