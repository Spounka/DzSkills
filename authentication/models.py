from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
def get_image_directory(instance, filename):
    return f'users/{instance.username}/images/profile_{filename}'


class User(AbstractUser):
    profile_image = models.ImageField(upload_to=get_image_directory, null=True)

# class SocialMediaLink(models.Model):
#     FACEBOOK = 'fb'
#     INSTAGRAM = 'ig'
#     BEHANCE = 'be'
#     LINKEDIN = 'li'
#     TWITTER = 'tw'
#
#     SOCIAL_MEDIA_CHOICES = [
#         (FACEBOOK, _('Facebook')),
#         (INSTAGRAM, _('INSTAGRAM')),
#         (BEHANCE, _('BEHANCE')),
#         (LINKEDIN, _('LinkedIn')),
#         (TWITTER, _('Twitter')),
#     ]
#
#     name = models.CharField(max_length=30, default=FACEBOOK, choices=SOCIAL_MEDIA_CHOICES)
#     url = models.CharField(max_length=300, default='')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
