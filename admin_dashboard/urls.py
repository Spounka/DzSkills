from django.urls import path
from . import views

urlpatterns = [
    path('receipts/', views.ListCreateReceipts.as_view(), name="receipts"),
    path('receipts/current/', views.RetrieveCurrentReceipt.as_view(), name="current-receipt"),
]
