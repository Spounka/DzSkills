from django.urls import path

from . import views

urlpatterns = [
    path('', views.StudentAPI.as_view(), name="students"),
    path('<int:pk>/', views.StudentAPI.as_view(), name="student"),
]
