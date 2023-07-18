from rest_framework import serializers

import courses.models
import support.models
from . import models
from .services import MessageService


class MessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'file']
        read_only_fileds = ['id']
        model = models.MessageFile

    def create(self, validated_data):
        return models.MessageFile.objects.create(message=validated_data['message'], file=validated_data['file'])


class MessageCreateSerializer(serializers.ModelSerializer):
    files = serializers.ListField(required=False, child=serializers.FileField(), write_only=True)
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=courses.models.Course.objects.filter(), write_only=True)
    ticket = serializers.PrimaryKeyRelatedField(queryset=support.models.Ticket.objects.filter(), write_only=True,
                                                required=False)

    class Meta:
        model = models.Message
        fields = ['id', 'content', 'date', 'files', 'sender', 'course', 'ticket', 'recipient']
        depth = 0

    def create(self, validated_data):
        request = self.context.get('request')
        sender = request.user
        recipient = validated_data.get('recipient')
        content = validated_data.get('content')
        files = validated_data.get('files')
        course = validated_data.get('course')
        ticket = validated_data.get('ticket')

        message = MessageService.create(
            sender=sender,
            recipient=recipient,
            content=content,
            course=course,
            ticket=ticket,
            files=files,
        )

        return message


class MessageSerializer(serializers.ModelSerializer):
    files = MessageFileSerializer(required=False, many=True)
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=courses.models.Course.objects.filter(), write_only=True)

    class Meta:
        model = models.Message
        fields = ['id', 'content', 'date', 'files', 'sender', 'course', 'recipient']
        depth = 0


class ConversationsSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    recipient = serializers.PrimaryKeyRelatedField(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'course', 'student', 'recipient', 'last_message']
        depth = 1
        model = models.Conversation

    def get_last_message(self, conversation):
        last_message = conversation.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
