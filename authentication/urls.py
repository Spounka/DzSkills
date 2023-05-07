from django.urls import path

from authentication import views

urlpatterns = [
    path('', views.GetAllUsersAPI.as_view(), name='users'),
    path('<int:pk>/', views.RetrieveUser.as_view(), name='user'),
]
