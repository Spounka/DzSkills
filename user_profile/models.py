from __future__ import annotations
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from authentication.models import User as UserModel


# Create your models here.
def get_image_directory(instance: 'UserProfile', filename):
    return f'users/{instance.user.username}/images/profile_{filename}'


class UserProfile(models.Model):
    user: 'UserModel' = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to=get_image_directory, null=True)

    description = models.CharField(max_length=300, blank=True, default="")
    nationality = models.CharField(max_length=30, blank=True, default="")
    speciality = models.CharField(max_length=30, blank=True, default="")

    def __str__(self):
        return self.user.username


class SocialMediaLink(models.Model):
    FACEBOOK = 'fb'
    INSTAGRAM = 'ig'
    LINKEDIN = 'li'
    BEHANCE = 'be'
    TWITTER = 'tw'

    SOCIAL_PLATFROM_CHOICES = [
        (FACEBOOK, _("Facebook")),
        (INSTAGRAM, _("Instagram")),
        (LINKEDIN, _("LinkedIn")),
        (BEHANCE, _("Behance")),
        (TWITTER, _("Twitter")),
    ]

    name = models.CharField(max_length=10, choices=SOCIAL_PLATFROM_CHOICES, default=FACEBOOK)
    url = models.URLField(max_length=300)
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="social_links")

    def __str__(self):
        return f'{self.profile.user.username} - {self.name}'
