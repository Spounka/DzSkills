from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from courses import models as courses


# Create your models here.
class Student(models.Model):
    user: settings.AUTH_USER_MODEL = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.CharField(max_length=300)
    nationality = models.CharField(max_length=30)
    speciality = models.CharField(max_length=30)

    courses = models.ManyToManyField(courses.Course, related_name='students')

    def __str__(self):
        return f'Student {self.user.username}'
