from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.http import HttpResponse
from rest_framework import response, generics
from . import serializers, models


# Create your views here.
class FacebookLoginView(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    # callback_url = 'http://localhost:8000/accounts/google/login/callback/'
    callback_url = 'http://localhost:8000/rest-auth/google/'
    client_class = OAuth2Client
    url = 'https://accounts.google.com/o/oauth2/v2/auth' \
          f'?redirect_uri={callback_url}' \
          '&prompt=consent&response_type=code' \
          '&client_id=497631069809-s8lrg6gs33p12mo7fuuola8occn2907p.apps.googleusercontent.com' \
          '&scope=openid%20email%20profile&access_type=offline'

    def get(self, request, *args, **kwargs):
        return response.Response(status=200, data=request.data)

    def post(self, request, *args, **kwargs):
        x = request
        return super().post(request, *args, **kwargs)


class GetAllUsersAPI(generics.ListAPIView):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()


def get_stuff(request):
    name = request.headers
    return HttpResponse(f'{request.GET.get("code")}')
