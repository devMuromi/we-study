from django.db import models


class Studyroom(models.Model):
    leader = models.ForeignKey("users.user", on_delete=models.CASCADE)

    studyroom_classification = models.CharField(max_length=64)
    studyroom_name = models.CharField(max_length=64)
    studyroom_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.studyroom_name

    class Meta:
        db_table = "Studyroom"
        verbose_name = "Studyroom"
        verbose_name_plural = "Studyroom"


class Calendar(models.Model):
    studyroom = models.ForeignKey("Studyroom", on_delete=models.CASCADE)
    date = models.DateField()


# 스터디룸마다 공통적으로 task가 있습니다. task 수행에 따라서 진도율이 증가합니다
# studyroom생성시 지정해야하며 추가는 가능하지만, 수정 삭제는 불가능
class Progress_task(models.Model):
    studyroom = models.ForeignKey("Studyroom", on_delete=models.CASCADE)
    task = models.TextField()
    taskNumber = models.PositiveIntegerField()


# 각 날짜에 들어갈 Todo입니다. 작성자, 내용, 학습시간, 수행한 task를 지정합니다
class Todo(models.Model):
    calendar = models.ForeignKey("Calendar", on_delete=models.CASCADE)
    writer = models.ForeignKey("users.user", on_delete=models.SET_NULL, null=True)
    content = models.TextField(null=True)
    learning_time = models.IntegerField()
    progress = models.IntegerField()


# 유저당 스터디룸에 하나씩 생기는 기록 모델입니다. m2m_changed signal이 적용되어 있습니다
class Progress_rate(models.Model):
    studyroom = models.ForeignKey("Studyroom", on_delete=models.CASCADE)
    user = models.ForeignKey("users.user", on_delete=models.CASCADE)
    totalHour = models.IntegerField(default=0)
    totalProgress = models.IntegerField(default=0)
