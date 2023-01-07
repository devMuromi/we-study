from django.db import models

# Create your models here.
class Application(models.Model):
    studyroomId = models.ForeignKey(
        "studyrooms.studyroom",
        on_delete=models.CASCADE,
        related_name="application",
    )

    userId = models.ForeignKey(
        "users.user",
        on_delete=models.CASCADE,
        related_name="application",
    )

    text = models.TextField()
