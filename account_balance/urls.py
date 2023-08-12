from django.urls import path
from . import views

urlpatterns = [
    path('', views.GetAccountBalance.as_view(), name="account-balance"),
    path('request/', views.RequestMoneyView.as_view(), name="request-money"),
    path('request/<int:pk>/accept/', views.ApproveMoneyRequest.as_view(), name="request-money"),
    path('request/<int:pk>/reject/', views.RejectMoneyRequest.as_view(), name="request-money"),
]
