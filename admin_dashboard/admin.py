from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.AdminConfig, admin.ModelAdmin)
admin.site.register(models.Receipt, admin.ModelAdmin)
admin.site.register(models.TitleScreenText, admin.ModelAdmin)
admin.site.register(models.CertificateTemplate, admin.ModelAdmin)
admin.site.register(models.LandingPageImage, admin.ModelAdmin)
