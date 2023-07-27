from allauth.account.models import EmailAddress
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models import Q
from django.utils import timezone
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
    is_favorite = models.BooleanField(default=False, verbose_name=_('Favorite'))

    instagram_link = models.CharField(max_length=300, default="", blank=True, null=True)
    facebook_link = models.CharField(max_length=300, default="", blank=True, null=True)
    twitter_link = models.CharField(max_length=300, default="", blank=True, null=True)
    linkedin_link = models.CharField(max_length=300, default="", blank=True, null=True)

    def update_average_rating(self) -> None:
        ratings = [course.average_rating for course in self.courses.all()]
        if len(ratings) > 0:
            average = sum(ratings) / len(ratings)
            self.average_rating = average

    def is_admin(self) -> bool:
        return self.groups.filter(name="AdminGroup").exists()

    def is_teacher(self) -> bool:
        return self.groups.filter(name="TeacherGroup").exists()

    def owns_course(self, course_id: int = 0) -> bool:
        if self.courses.filter(pk=course_id).exists():
            return True
        query = self.order_set.filter(course_id=course_id)
        if query.exists() and query.filter(payment__status='a'):
            return True
        return False

    def is_banned(self):
        bans = self.bans.filter(duration__gt=timezone.now())
        return bans.exists()

    def get_last_ban(self):
        return self.bans.filter(duration__gt=timezone.now()).first()

    @classmethod
    def get_site_admin(cls) -> 'User':
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
            user.emailaddress_set.add(EmailAddress.objects.create(email=user.email, verified=True, primary=True))
            user.save()
            return user
