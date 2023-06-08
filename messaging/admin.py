from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Message, admin.ModelAdmin)
admin.site.register(models.MessageFile, admin.ModelAdmin)
admin.site.register(models.Conversation, admin.ModelAdmin)
