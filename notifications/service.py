import json
from typing import Any

from django.contrib.auth import get_user_model

from . import models

UserModel = get_user_model()


class NotificationService:

    @classmethod
    def create(cls, sender: UserModel = None, recipient_user: UserModel = None, notification_type: str = '',
               extra_data: dict[str, Any] = None) -> None | models.Notification:
        if (sender is None) ^ (recipient_user is None):
            raise ValueError('Must provide at a sender or a recipient')
        if recipient_user.is_admin():
            recipient = UserModel.get_site_admin()
        else:
            recipient = recipient_user
        notification = models.Notification.objects.create(
            sender=sender,
            recipient=recipient,
            notification_type=notification_type,
            extra_data=extra_data
        )
        return notification
