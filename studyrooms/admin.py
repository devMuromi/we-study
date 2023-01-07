from django.contrib import admin
from .models import *

admin.site.register(Studyroom)
admin.site.register(Calendar)
admin.site.register(Progress_task)
admin.site.register(Todo)
admin.site.register(Progress_rate)


class StudyroomAdmin(admin.ModelAdmin):
    pass
