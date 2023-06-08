from rest_framework import serializers

from authentication.serializers import UserSerializer
from . import models


class CommentSerializer(serializers.ModelSerializer):
    commentor = UserSerializer()

    class Meta:
        model = models.Comment
        depth = 0
        fields = ['id', 'content', 'commentor', 'video']


class CommentCreationSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data['commentor'] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        model = models.Comment
        depth = 0
        fields = ['id', 'content', 'video']
