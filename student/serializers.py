from django.contrib.auth import get_user_model
from rest_framework import serializers
from . import models
from django.conf import settings

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        depth = 1
        fields = ['pk', 'username', 'first_name', 'last_name', 'email', 'profile_image']


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.Student
        depth = 1
        # exclude = ['password']
        fields = "__all__"
