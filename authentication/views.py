from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.shortcuts import redirect
from rest_framework import response, generics, permissions, status, views
from rest_framework.decorators import api_view, permission_classes
from django.utils.translation import gettext_lazy as _

from . import serializers, models
from .permissions import IsAdmin

PASSWORDS_DONT_MATCH_ERROR = _("Passwords don't match")


# Create your views here.
class FacebookLoginView(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://localhost:3000/register/google/'
    client_class = OAuth2Client


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

    # noinspection PyMethodMayBeStatic
    def update(self, request, *args, **kwargs):
        instance = request.user
        validated_data = {'old_password': request.data.get('old_password', ''),
                          'password1': request.data.get('password1'),
                          'password2': request.data.get('password2')}
        if not instance.check_password(validated_data['old_password']):
            make_password(password=validated_data['old_password'])
            return response.Response(data={"message": "Wrong Password"}, status=status.HTTP_400_BAD_REQUEST)
        if validated_data['password1'] != validated_data['password2']:
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
    permission_classes = [IsAdmin]

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password1')
        password2 = request.data.get('password2')
        email = request.data.get('email')
        profile_image = request.data.get('profile_image')
        if password != password2:
            make_password(password)
            return response.Response(status=status.HTTP_400_BAD_REQUEST, data={'message': PASSWORDS_DONT_MATCH_ERROR})
        user = models.User.objects.create(username=username, email=email,
                                          profile_image=profile_image)
        user.set_password(password)
        user.groups.add(Group.objects.get(name="AdminGroup"))
        user.save()
        user.emailaddress_set.add(EmailAddress.objects.create(email=user.email, verified=True))
        user.save()

        return response.Response(status=status.HTTP_201_CREATED, data={'id': user.pk})


class CreateNewTeacher(views.APIView):
    permission_classes = [IsAdmin]

    # noinspection PyMethodMayBeStatic
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        user_query = models.User.objects.filter(username=username)
        if user_query.exists():
            return response.Response(status=status.HTTP_400_BAD_REQUEST,
                                     data={'message': _("a user with that username already exists")})
        password = request.data.get('password1')
        password2 = request.data.get('password2')
        email = request.data.get('email')
        if models.User.objects.filter(email=email).exists():
            return response.Response(status=status.HTTP_400_BAD_REQUEST,
                                     data={'message': _("A user is already registered with this e-mail address.")})
        profile_image = request.data.get('profile_image')
        if password != password2:
            make_password(password)
            return response.Response(status=status.HTTP_400_BAD_REQUEST, data={'message': PASSWORDS_DONT_MATCH_ERROR})
        user = models.User.objects.create(username=username, email=email,
                                          profile_image=profile_image)
        user.set_password(password)
        user.groups.add(Group.objects.get(name="TeacherGroup"))
        user.save()
        user.emailaddress_set.add(EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True))
        user.save()

        return response.Response(status=status.HTTP_201_CREATED, data={'id': user.pk})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_usernames(request):
    usernames = models.User.objects.all()
    serializer = serializers.UsernamesSerializer(usernames, many=True)
    return response.Response(status=status.HTTP_200_OK, data=serializer.data)


@api_view(['POST'])
@permission_classes([IsAdmin])
def make_user_favorite(request, *args, **kwargs):
    pk = kwargs.get('pk')
    if not pk:
        return response.Response(status=status.HTTP_400_BAD_REQUEST,
                                 data={'code': 'no_id', 'message': _('No ID provided')})
    try:
        user = models.User.objects.get(pk=pk)
        if not user.is_teacher():
            return response.Response(status=status.HTTP_400_BAD_REQUEST,
                                     data={'code': 'user_not_teacher', 'message': _('User is not a mentor')})
        user.is_favorite = not user.is_favorite
        user.save()
        return response.Response(status=status.HTTP_200_OK, data=serializers.UserSerializer(user).data)
    except models.User.DoesNotExist:
        return response.Response(status=status.HTTP_400_BAD_REQUEST,
                                 data={'code': 'no_user_found', 'message': _('No User with such ID')})


class GetDzSkillsAdmin(generics.RetrieveAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.get_queryset().filter(pk=models.User.get_site_admin().pk).first()


def password_reset_view(request, *args, **kwargs):
    return redirect(f'/password-forgotten/confirm/?u={kwargs.get("uidb64")}&t={kwargs.get("token")}', )
    # return redirect('/password-forgotten/', kwargs={'u': kwargs.get('uidb64'), 't': kwargs.get('token')},
    #                 permanent=True)
