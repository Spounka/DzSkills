from django.contrib import admin
from .models import Payment, Order

# Register your models here.
admin.site.register(Order, admin.ModelAdmin)
admin.site.register(Payment, admin.ModelAdmin)
