from django.contrib.auth import get_user_model

from . import models
from rest_framework import serializers

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['pk', 'first_name', 'last_name', 'profile_image']


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(required=False)
    recipient = UserSerializer(required=False)

    class Meta:
        model = models.Notification
        fields = '__all__'
        depth = 3
