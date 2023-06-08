from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateComment.as_view(), name="create-comment"),
    path('video/<int:pk>/', views.GetCommentsFromVideo.as_view(), name="comment-from-video"),
    path('<int:pk>/', views.UpdateDeleteComment.as_view(), name="edit-comment")
]
