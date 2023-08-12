from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from authentication import views
from backend import settings

urlpatterns = [
    path('api/admin/', admin.site.urls),

    # path('api/accounts/', include('allauth.urls'), name="socialaccount_signup"),
    path('api/rest-auth/', include('dj_rest_auth.urls')),
    path('api/rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/rest-auth/facebook/', views.FacebookLoginView.as_view(), name='fb_login'),
    path('api/rest-auth/google/', views.GoogleLogin.as_view(), name='google_login'),

    path('api/users/', include('authentication.urls')),
    path('api/courses/', include('courses.urls'), name="courses"),
    path('api/orders/', include('course_buying.urls'), name="orders"),
    path('api/balance/', include('account_balance.urls'), name="balance"),
    path('api/configs/', include('admin_dashboard.urls'), name="configs"),
    path('api/comments/', include('comment.urls'), name="comments"),
    path('api/conversations/', include('messaging.urls'), name="conversations"),
    path('api/support/', include('support.urls')),
    path('api/ban/', include('ban.urls')),
    path('api/notifications/', include('notifications.urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
