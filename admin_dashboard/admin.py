from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.AdminConfig, admin.ModelAdmin)
admin.site.register(models.Receipt, admin.ModelAdmin)
