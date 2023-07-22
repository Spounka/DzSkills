from django.db.models import Q

from authentication.models import User
from . import models
from messaging.models import Conversation
from messaging.services import ConversationService, MessageService

from django.utils.translation import gettext_lazy as _


class TicketService:
    @classmethod
    def get_or_create(cls, sender: User, conversation: Conversation = None):
        ticket = None
        if conversation:
            ticket = models.Ticket.objects.filter(conversation=conversation, sender=sender)
        if not ticket:
            ticket = models.Ticket.objects.create()
            dzskills_user = User.get_site_admin()
            convo = ConversationService.get_or_create(sender, recipient=dzskills_user, ticket=ticket)
            ticket.conversation = convo
            ticket.save()
            content = _('Hello, How can I help you?')
            MessageService.create(sender=User.get_site_admin(), recipient=sender, ticket=ticket,
                                  content=content)

        return ticket
