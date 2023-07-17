from django.urls import path

from authentication import views

urlpatterns = [
    path('', views.GetAllUsersAPI.as_view(), name='users'),
    path('usernames/', views.get_usernames, name='usernames'),
    path('admin/', views.GetDzSkillsAdmin.as_view()),
    path('admin/create/', views.CreateNewAdmin.as_view(), name='admin-create'),
    path('teacher/create/', views.CreateNewTeacher.as_view(), name='admin-create'),
    path('<int:pk>/', views.RetrieveUser.as_view(), name='user'),
    path('<int:pk>/password/update/', views.UpdatePassword.as_view(), name='update-password'),
    # re_path(r'^reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', views.password_reset_view,
    #         name='password_reset_confirm'),
]
