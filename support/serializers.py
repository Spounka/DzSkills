from rest_framework import serializers

from .services import TicketService
from . import models
import messaging.serializers


class TicketSerializer(serializers.ModelSerializer):
    conversation = messaging.serializers.ConversationsSerializer()

    class Meta:
        model = models.Ticket
        fields = "__all__"
        depth = 1

    def create(self, validated_data):
        validated_data['sender'] = self.context.get('request').user
        return TicketService.create(**validated_data)
