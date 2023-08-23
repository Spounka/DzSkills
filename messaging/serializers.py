from rest_framework import serializers

import courses.models
import courses.serializers
import support.models
from . import models
from .services import MessageService
import authentication.serializers
from authentication.models import User
from django.utils.translation import gettext_lazy as _


class MessageFileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'file']
        read_only_fileds = ['id']
        model = models.MessageFile

    def create(self, validated_data):
        return models.MessageFile.objects.create(message=validated_data['message'], file=validated_data['file'])


class MessageCreateSerializer(serializers.ModelSerializer):
    files = serializers.ListField(
        required=False, child=serializers.FileField(), write_only=True)
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=courses.models.Course.objects.filter(), write_only=True,
                                                required=False)
    ticket = serializers.PrimaryKeyRelatedField(queryset=support.models.Ticket.objects.filter(), write_only=True,
                                                required=False)
    type = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = models.Message
        fields = ['id', 'content', 'date', 'files', 'sender',
                  'course', 'ticket', 'recipient', 'type']

        depth = 0

    def create(self, validated_data):
        request = self.context.get('request')
        if validated_data.get('type', None):
            sender = User.get_site_admin()
            content = validated_data.get(_('Hello, How can I help you?'))
            recipient = request.user
        else:
            sender = request.user
            content = validated_data.get('content')
            recipient = validated_data.get('recipient')
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
    course = serializers.PrimaryKeyRelatedField(
        queryset=courses.models.Course.objects.filter(), write_only=True)

    class Meta:
        model = models.Message
        fields = ['id', 'content', 'date', 'files',
                  'sender', 'course', 'recipient']
        depth = 0


class ConversationsSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    recipient = serializers.PrimaryKeyRelatedField(read_only=True)
    last_message = serializers.SerializerMethodField(read_only=True)
    course_title = serializers.SerializerMethodField(read_only=True)
    course_owner = serializers.SerializerMethodField(read_only=True)
    student_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ['id', 'course', 'student', 'recipient', 'ticket', 'last_message', 'course_title', 'course_owner',
                  'student_data']
        depth = 1
        model = models.Conversation

    def get_last_message(self, conversation):
        last_message = conversation.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_course_title(self, instance):
        if instance.course:
            return courses.serializers.CourseListSerializer(instance.course, context={"request": self.context.get('request', None)}).data.get('title')
        return ''

    def get_course_owner(self, instance):
        if instance.course:
            return courses.serializers.CourseListSerializer(instance.course, context=self.context).data.get('owner')
        elif hasattr(instance, 'ticket'):
            return authentication.serializers.UserSerializer(User.get_site_admin(), context=self.context).data
        return ''

    def get_student_data(self, instance):
        return authentication.serializers.UserSerializer(instance.student, context=self.context).data
