from django.urls import path

from authentication import views

urlpatterns = [
    path('', views.GetAllUsersAPI.as_view(), name='users'),
    path('admin/create/', views.CreateNewAdmin.as_view(), name='admin-create'),
    path('<int:pk>/', views.RetrieveUser.as_view(), name='user'),
    path('<int:pk>/password/update/', views.UpdatePassword.as_view(), name='update-password'),
]
