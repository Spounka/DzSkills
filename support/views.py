from rest_framework import status, response, generics, viewsets, permissions
from . import models, serializers
import messaging.serializers
import messaging.models


class TicketCreate(generics.CreateAPIView):
    serializer_class = serializers.TicketSerializer
    queryset = models.Ticket.objects.all()
    permission_classes = [permissions.IsAuthenticated, ]


class RetrieveUpdateTicket(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.TicketSerializer
    queryset = models.Ticket.objects.all()


class GetSupportConversationAPIView(generics.RetrieveAPIView):
    serializer_class = messaging.serializers.ConversationsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.get_queryset()

    def get_queryset(self):
        student = self.request.user
        try:
            ticket = models.Ticket.objects.get(pk=self.kwargs.get('pk'))
            conversation = messaging.models.Conversation.objects.filter(student=student, ticket=ticket)
            query = conversation.first()
            return query
        except models.Ticket.DoesNotExist:
            return None
