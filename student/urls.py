from django.urls import path

from . import views

urlpatterns = [
    path('', views.StudentAPI.as_view(), name="student")
]
