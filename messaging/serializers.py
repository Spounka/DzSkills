from rest_framework import serializers

import courses.serializers, courses.models
from . import models
from .services import MessageService
from authentication.serializers import UserSerializer


class MessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'file']
        model = models.MessageFile


class MessageSerializer(serializers.ModelSerializer):
    files = MessageFileSerializer(many=True, required=False)
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=courses.models.Course.objects.filter(), write_only=True)

    class Meta:
        model = models.Message
        fields = ['id', 'content', 'date', 'files', 'sender', 'course', 'recipient']
        depth = 0

    def create(self, validated_data):
        request = self.context.get('request')
        sender = request.user
        recipient = validated_data.get('recipient')
        content = validated_data.get('content')
        files = validated_data.get('files')
        course = validated_data.get('course')

        message = MessageService.create(
            sender=sender,
            recipient=recipient,
            content=content,
            files=files,
            course=course,
        )

        return message


class ConversationsSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    teacher = serializers.PrimaryKeyRelatedField(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'course', 'student', 'teacher', 'last_message']
        depth = 1
        model = models.Conversation

    def get_last_message(self, conversation):
        last_message = conversation.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
