from rest_framework import serializers

from .services import TicketService
from . import models
import messaging.serializers
import messaging.models
import courses.models
import authentication.serializers


class CourseSerializer(serializers.ModelSerializer):
    owner = authentication.serializers.UserSerializer(read_only=True)

    class Meta:
        model = courses.models.Course
        fields = ['id', 'owner', 'title']
        read_only_fields = ('average_rating',)
        depth = 1


class ConversationSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    recipient = serializers.PrimaryKeyRelatedField(read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'course', 'student', 'recipient', 'ticket', 'last_message']
        depth = 1
        model = messaging.models.Conversation

    def get_last_message(self, conversation):
        last_message = conversation.messages.last()
        if last_message:
            return messaging.serializers.MessageSerializer(last_message).data
        return None


class TicketSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer(required=False)
    state = serializers.CharField(required=False)

    class Meta:
        model = models.Ticket
        fields = "__all__"
        depth = 1

    def create(self, validated_data):
        validated_data['sender'] = self.context.get('request').user
        validated_data.pop('date', None)
        return TicketService.get_or_create(**validated_data)
