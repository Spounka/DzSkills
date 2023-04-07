from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers
from authentication.serializers import UserSerializer

import authentication.serializers
from .models import UserProfile, SocialMediaLink

UserModel = get_user_model()


class SocialMediaLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaLink
        exclude = ('profile',)


class UserProfileSerializer(serializers.ModelSerializer):
    user = authentication.serializers.UserSerializer()
    social_links = SocialMediaLinkSerializer(many=True, required=False)

    def create(self, validated_data: dict[str, Any]):
        user_data = validated_data.pop('user')
        user = UserModel.objects.create(**user_data)
        user.save()
        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data: dict[str, Any]):
        social_media_links_data = validated_data.pop('social_links', None)
        user_data = validated_data.pop('user', None)

        # social_links_serializer = SocialMediaLinkSerializer(instance.social_links.all(), data=social_media_links_data,
        #                                                     many=True)

        # if social_links_serializer.is_valid(raise_exception=True):
        #     social_links_serializer.save()

        user_serializer = UserSerializer(instance.user, data=user_data)
        if user_serializer.is_valid():
            user_serializer.save()
        return super().update(instance, **validated_data)

    class Meta:
        model = UserProfile
        # exclude = ('user',)
        fields = '__all__'
