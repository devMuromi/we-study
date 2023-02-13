from django.contrib import admin
from .models import Studyroom, Task, Study, StudyroomInfo, Application

admin.site.register(Studyroom)
admin.site.register(Task)
admin.site.register(Study)
admin.site.register(StudyroomInfo)
admin.site.register(Application)


class StudyroomAdmin(admin.ModelAdmin):
    pass
