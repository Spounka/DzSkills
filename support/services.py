from django.db.models import Q

from authentication.models import User
from . import models


class MessageService:
    @classmethod
    def create(cls, sender: User, content: str, ticket: models.Ticket, files=None):
        conversation = models.Conversation.objects.filter(
            sender=sender).filter(ticket=ticket).first()
        if not conversation:
            conversation = models.Conversation.objects.create(
                sender=sender,
                ticket=ticket
            )
        message = models.Message.objects.create(
            content=content,
            conversation=conversation,
            sender=sender,
        )
        if files:
            message_files = [models.MessageFile(message=message, file=file) for file in files]
            models.MessageFile.objects.bulk_create(message_files)

        return message
