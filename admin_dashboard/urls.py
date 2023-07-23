from django.urls import path
from . import views

urlpatterns = [
    path('', views.RetrieveUpdateAdminSettingsView.as_view(), name="admin"),
    path('receipts/', views.ListCreateReceipts.as_view(), name="receipts"),
    path('receipts/delete/', views.ReceiptsDelete.as_view(), name="receipts"),
    path('receipts/<int:pk>/', views.UpdateDestroyReceipt.as_view(), name='update-destroy-receipt'),
    path('receipts/current/', views.RetrieveCurrentReceipt.as_view(), name="current-receipt"),
]
