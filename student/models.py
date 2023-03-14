from django.db import models
from django.conf import settings


# Create your models here.
class Student(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.CharField(max_length=300)
    nationality = models.CharField(max_length=30)
    speciality = models.CharField(max_length=30)

    def __str__(self):
        return f'Student {self.user.username}'
