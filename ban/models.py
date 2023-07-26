import datetime
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

UserModel = get_user_model()


# Create your models here.
class Ban(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='bans')
    duration = models.DateField(default=lambda: timezone.now() + timedelta(days=1))
