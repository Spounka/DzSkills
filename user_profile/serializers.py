from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from authentication.serializers import UserSerializer
from django.conf import settings

import authentication.serializers
from .models import UserProfile, SocialMediaLink

UserModel = get_user_model()


class SocialMediaLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaLink
        exclude = ('profile',)


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    social_links = SocialMediaLinkSerializer(many=True, required=False)

    class Meta:
        model = UserProfile
        # exclude = ('user',)
        fields = '__all__'

    def create(self, validated_data: dict[str, Any]):
        user = validated_data.pop('user', None)
        if not user:
            raise ValidationError('user does not exist')
        social_links = validated_data.pop('social_links')
        profile = UserProfile.objects.create(user=user, **validated_data)
        socials = SocialMediaLinkSerializer(data=social_links, many=True)
        socials.is_valid(raise_exception=True)
        links = [SocialMediaLink.objects.create(profile=profile, **data) for data in socials.validated_data]
        profile.social_links.set(links)
        return profile

    def update(self, instance: UserProfile, validated_data: dict[str, Any]):
        social_media_links_data = validated_data.pop('social_links', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        if social_media_links_data:
            for social_link_data in social_media_links_data:
                name, url = social_link_data['name'], social_link_data['url']
                if instance.social_links.filter(name=name).first():
                    instance.social_links.get(name=name).url = url
                else:
                    instance.social_links.add(SocialMediaLink.objects.create(profile=instance, name=name, url=url))

        return instance
