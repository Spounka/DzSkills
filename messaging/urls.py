from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.ConversationsListAPIView.as_view(), name="conversations"),
    path('get/<int:pk>/', views.GetTeacherStudentConversationAPIView.as_view(), name="conversation"),
    path('messages/', views.MessagesCreateAPIView.as_view(), name="create-message"),
    path('<int:pk>/', views.MessagesListAPIView.as_view(), name="view-messages"),
    path('<int:pk>/files/', views.download_message_files, name="download-files"),
]
