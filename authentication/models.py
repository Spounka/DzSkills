from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


# Create your models here.
def get_image_directory(instance, filename):
    return f'users/{instance.username}/images/profile_{filename}'


class User(AbstractUser):
    profile_image = models.ImageField(upload_to=get_image_directory, null=True, verbose_name=_('Profile Image'))
    description = models.CharField(max_length=300, default="", verbose_name=_("Description"))
    nationality = models.CharField(max_length=300, default="", verbose_name=_('Nationality'))
    speciality = models.CharField(max_length=300, default="", verbose_name=_('Speciality'))

    average_rating = models.FloatField(default=0.0, verbose_name=_('Average Rating'))

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

    @classmethod
    def get_site_admin(cls):
        try:
            return cls.objects.get(username='dzskills')
        except cls.DoesNotExist:
            user = User(
                username='dzskills',
                first_name='DzSkills',
                last_name="",
                email='contact@dzskills.com',
                description="DzSkills",
                nationality='Algerian',
                speciality='Teach'
            )
            user.set_password('rootuser')
            user.profile_image.save(name='dzskills.png', content=open('logo.png', 'rb'))
            user.save()
            user.groups.add(Group.objects.get(name="AdminGroup"))
            user.emailaddress_set.first().verified = True
            user.save()
            return user
