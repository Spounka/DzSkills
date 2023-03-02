from django.contrib import admin
from django.urls import path, include

from authentication import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/rest-auth/', include('dj_rest_auth.urls')),
    path('api/rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/rest-auth/facebook/', views.FacebookLoginView.as_view(), name='fb_login'),
    path('api/rest-auth/google/', views.GoogleLogin.as_view(), name='google_login'),
]
