from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Application)


class ApplicationsAdmin(admin.ModelAdmin):
    pass
