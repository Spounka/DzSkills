from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


# Create your models here.
def get_image_directory(instance, filename):
    return f'users/{instance.username}/images/profile_{filename}'


class User(AbstractUser):
    profile_image = models.ImageField(upload_to=get_image_directory, null=True)
    description = models.CharField(max_length=300, default="")
    nationality = models.CharField(max_length=300, default="")
    speciality = models.CharField(max_length=300, default="")

    average_rating = models.FloatField(default=0.0)

    def update_average_rating(self):
        ratings = [course.average_rating for course in self.courses.all()]
        if len(ratings) > 0:
            average = sum(ratings) / len(ratings)
            self.average_rating = average

    def is_admin(self):
        return self.groups.filter(name="AdminGroup").exists()

    def is_teacher(self):
        return self.groups.filter(name="TeacherGroup").exists()

    def owns_course(self, course_id: int = 1, course=None) -> bool:
        query = self.order_set.filter(Q(course_id=course_id) | Q(course=course))
        if query.exists() and query.filter(payment__status='a'):
            return True
        return False
