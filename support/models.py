from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import messaging.models

# Create your models here.
UserModel = get_user_model()


class Ticket(models.Model):
    OPEN = 'o'
    CLOSED = 'c'

    STATES = (
        (OPEN, _('Open')),
        (CLOSED, _('Closed')),
    )
    state = models.CharField(choices=STATES, default=OPEN, max_length=30)
    date = models.DateTimeField(default=timezone.now)
    conversation = models.OneToOneField(messaging.models.Conversation, on_delete=models.SET_NULL, null=True, blank=True)
