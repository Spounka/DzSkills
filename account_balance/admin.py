from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.MoneyRequest, admin.ModelAdmin)
admin.site.register(models.AccountBalance, admin.ModelAdmin)
