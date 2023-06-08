from django.contrib import admin
from .models import UserProfile, SocialMediaLink

# Register your models here.
admin.site.register(UserProfile, admin.ModelAdmin)
admin.site.register(SocialMediaLink, admin.ModelAdmin)
