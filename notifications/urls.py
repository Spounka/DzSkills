from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationsAPIView.as_view(), name="user-notifications"),
    path('read/', views.mark_notifications_as_read, name='mark-notifications-as-read'),
]
