from authentication.models import User
from . import models
from messaging.models import Conversation


class TicketService:
    @classmethod
    def get_or_create(cls, sender: User, conversation: Conversation = None):
        ...
