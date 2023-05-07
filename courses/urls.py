from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.CourseAPI.as_view(), name="courses-list"),
    path('<int:pk>/', views.CourseAPI.as_view(), name="course"),
    path('<int:pk>/students/', views.GetCourseStudents.as_view(), name="course"),

    path('trending/', views.TrendingCourses.as_view(), name="trending-courses"),

    path('<int:pk>/chapters/', views.ChapterAPI.as_view(), name="chapters"),
    path('<int:pk>/chapters/<int:ch>/videos', views.VideoAPI.as_view(), name="video"),

    path('progress/', views.StudentProgressAPI.as_view(), name='progressions'),
    path('progress/<int:pk>/', views.StudentProgressAPI.as_view(), name='progression'),
    path('progress/<int:pk>/update/', views.UpdateProgressAPI.as_view(), name='update-progress'),
]
