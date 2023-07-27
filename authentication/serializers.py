from allauth.account.models import EmailAddress
from dj_rest_auth.serializers import PasswordResetSerializer
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

import authentication.forms
from .models import User as UserModel

try:
    from allauth.account import app_settings as allauth_account_settings
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.socialaccount.helpers import complete_social_login
    from allauth.socialaccount.models import SocialAccount
    from allauth.socialaccount.providers.base import AuthProcess
    from allauth.utils import email_address_exists, get_username_max_length
    from allauth.account.adapter import get_adapter
except ImportError:
    raise ImportError('allauth needs to be added to INSTALLED_APPS.')


class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    email = serializers.EmailField(required=allauth_account_settings.EMAIL_REQUIRED)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_account_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _('A user is already registered with this e-mail address.'),
                )
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def custom_signup(self, request, user):
        # TODO: Implement the function to fix Facebook / Google Signup
        pass

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
        }

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def create(self, validated_data):
        return super().create(validated_data)

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data['password1'], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.save()
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class UserPasswordResetSerializer(PasswordResetSerializer):
    @property
    def password_reset_form_class(self):
        if 'allauth' in settings.INSTALLED_APPS:
            return authentication.forms.PasswordResetForm
        else:
            return PasswordResetForm


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    email_valid = serializers.SerializerMethodField(read_only=True)
    is_banned = serializers.SerializerMethodField(read_only=True)
    last_ban = serializers.SerializerMethodField(read_only=True)

    # profile_image = serializers.SerializerMethodField(read_only=True)
    is_favorite = serializers.BooleanField(required=False)

    class Meta:
        model = UserModel
        depth = 1
        fields = ('pk', 'username', 'email', 'email_valid', 'first_name', 'last_name',
                  'date_joined', 'profile_image', 'description', 'speciality', 'nationality', 'instagram_link',
                  'facebook_link', 'twitter_link', 'linkedin_link', 'is_favorite', 'average_rating', 'is_banned',
                  'last_ban', 'groups',)
        read_only_fields = ['average_rating']

    #
    # def get_profile_image(self, user: UserModel):
    #     if user.is_admin():
    #         return f'http://localhost:8000{user.profile_image.url}'
    #     return f'https://picsum.photos/1024/1024?random={user.pk}'

    def get_email_valid(self, user):
        email = EmailAddress.objects.filter(email=user.email, verified=True)
        return email.exists()

    def get_is_banned(self, user):
        return user.is_banned()

    def get_last_ban(self, user):
        if not user.is_banned():
            return None
        return user.get_last_ban().duration


class UsernamesSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = UserModel
        fields = ['id', 'username', 'groups']
        depth = 1
