from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.CourseAPI.as_view(), name="video-list"),
    path('<int:pk>/chapters/', views.ChapterAPI.as_view(), name="chapters"),
    path('<int:pk>/chapters/<int:ch>/videos', views.VideoAPI.as_view(), name="video"),
]
