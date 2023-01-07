from django.contrib import admin
from .models import Studyroom, Schedule, Task, Study, StudyroomInfo

admin.site.register(Studyroom)
admin.site.register(Schedule)
admin.site.register(Task)
admin.site.register(Study)
admin.site.register(StudyroomInfo)


class StudyroomAdmin(admin.ModelAdmin):
    pass
