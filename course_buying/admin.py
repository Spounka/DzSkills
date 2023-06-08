from django.contrib import admin
from .models import Payment, Order


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = ('course', 'buyer', 'date_issued',)


# admin.site.register(Order, admin.ModelAdmin)
admin.site.register(Payment, admin.ModelAdmin)
