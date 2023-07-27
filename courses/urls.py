from django.urls import path

from . import views

urlpatterns = [
    path('', views.CourseAPI.as_view(), name="courses-list"),
    path('most-sold/', views.MostSoldCourses.as_view(), name="most-sold-courses"),
    path('<int:pk>/', views.CourseAPI.as_view(), name="course"),
    path('<int:pk>/flip-trending/', views.make_course_favourite, name="course-favourite"),
    path('<int:pk>/flip/', views.CourseStateUpdate.as_view(), name="course-flip-state"),
    path('<int:pk>/students/', views.GetCourseStudents.as_view(), name="course-students"),
    path('<int:pk>/students/remove/', views.RemoveStudentsFromCourseAPI.as_view(), name='remove-students'),

    path('categories/', views.GetCategoryAPI.as_view(), name='categories'),
    path('levels/', views.GetLevelsAPI.as_view(), name='levels'),
    path('hashtags/', views.GetHashtagsAPI.as_view(), name="hashtags"),
    path('levels/<int:pk>/', views.EditDeleteLevel.as_view(), name='levels'),
    path('hashtags/<int:pk>/', views.EditDeleteHashtag.as_view(), name="hashtags"),
    path('categories/<int:pk>/', views.EditDeleteCategory.as_view(), name='categories'),
    path('hashtags/delete/', views.HashtagsDelete.as_view(), name="hashtags"),
    path('levels/delete/', views.LevelsDelete.as_view(), name='levels'),

    path('trending/', views.TrendingCourses.as_view(), name="trending-courses"),

    path('<int:pk>/chapters/', views.ChapterAPI.as_view(), name="chapters"),
    path('<int:pk>/chapters/<int:ch>/videos/', views.VideoAPI.as_view(), name="video"),

    path('progress/', views.StudentProgressAPI.as_view(), name='progressions'),
    path('progress/<int:pk>/', views.StudentProgressAPI.as_view(), name='progression'),
    path('progress/<int:pk>/update/', views.UpdateProgressAPI.as_view(), name='update-progress'),

    path('owner/<int:pk>/related/', views.GetRelatedCourses.as_view(), name='related-courses'),
    path('student/related/', views.GetStudentCourses.as_view(), name='student-reltated-courses'),
    path('student/<int:pk>/related/', views.GetStudentCourses.as_view(), name='student-reltated-courses'),

    path('<int:pk>/quizz/', views.QuizzRetrieveUpdateDestroyView.as_view(), name="quizz-list-create"),

    path('<int:pk>/certificate/', views.GetCertificate.as_view(), name="certificate"),
    path('<int:pk>/ratings/', views.ListCreateRatings.as_view(), name="ratings"),
    path('<int:pk>/<str:status>/', views.CourseStatusUpdateAPI.as_view(), name="update-course-status"),

]
