from django.contrib import admin
from django.urls import path, include

from authentication import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('rest-auth/', include('dj_rest_auth.urls')),
    path('rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('rest-auth/facebook/', views.FacebookLoginView.as_view(), name='fb_login'),
    path('rest-auth/google/', views.GoogleLogin.as_view(), name='google_login'),
]
