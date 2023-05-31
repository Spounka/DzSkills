from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth.hashers import make_password
from rest_framework import response, generics, permissions, status, views

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


class RetrieveUser(generics.RetrieveAPIView):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class UpdatePassword(views.APIView):
    queryset = models.User.objects.all()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = request.user
        validated_data = {'old_password': request.data.get('old_password'), 'password1': request.data.get('password1'),
                          'password2':    request.data.get('password2')}
        if not instance.check_password(validated_data['old_password']):
            make_password(password=validated_data['old_password'])
            return response.Response(data={"message": "Wrong Password"}, status=status.HTTP_400_BAD_REQUEST)
        if not validated_data['password1'] == validated_data['password2']:
            make_password(password=validated_data['old_password'])
            return response.Response(data={"message": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
        instance.set_password(validated_data['password1'])
        instance.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return response.Response(status=status.HTTP_204_NO_CONTENT)


class CreateNewAdmin(views.APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password1')
        password2 = request.data.get('password2')
        email = request.data.get('email')
        profile_image = request.data.get('profile_image')
        if not password == password2:
            make_password(password)
            return response.Response(status=status.HTTP_400_BAD_REQUEST, data={'message': "Passwords don't match"})
        user = models.User.objects.create(username=username, email=email,
                                          profile_image=profile_image)
        user.set_password(password)
        user.save()

        return response.Response(status=status.HTTP_201_CREATED, data={'id': user.pk})
