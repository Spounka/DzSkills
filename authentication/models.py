from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
def get_image_directory(instance, filename):
    return f'users/{instance.username}/images/profile_{filename}'


class User(AbstractUser):
    profile_image = models.ImageField(upload_to=get_image_directory, null=True)
