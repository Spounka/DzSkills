from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
def get_course_image_upload_directory(instance, filename):
    return f'{instance.owner}/courses/{instance.title}/thumbnail/{filename}'


def get_course_file_upload_directory(instance, filename):
    return f'{instance.owner}/courses/{instance.title}/presentation/{filename}'


def get_video_upload_directory(instance, filename):
    return f'{instance.chapter.course.owner}/courses/{instance.chapter.course.title}/chapter_{instance.chapter.title}' \
           f'/videos/{filename}'


def get_chapter_upload_directory(instance, filename):
    return f'{instance.course.owner}/courses/{instance.course.title}/chapter_{instance.title}/{filename}'


class Course(models.Model):
    PENDING = 'pend'
    ACCEPTED = 'acc'
    REFUSED = 'ref'

    STATUS_CHOICES = [
        (PENDING, _("Pending")),
        (ACCEPTED, _("Accepted")),
        (REFUSED, _("Refused")),
    ]

    title = models.CharField(max_length=300)
    description = models.CharField(max_length=150)
    thumbnail = models.ImageField(upload_to=get_course_image_upload_directory)
    price = models.PositiveIntegerField()
    hastags = models.CharField(max_length=100)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=PENDING)

    presentation_file = models.FileField(upload_to=get_course_file_upload_directory, blank=True, null=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses")

    def accept_course(self):
        self.status = self.ACCEPTED
        self.save()

    def refuse_title(self):
        self.status = self.REFUSED
        self.save()

    def __str__(self):
        return self.title


class Chapter(models.Model):
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=150)
    thumbnail = models.ImageField(upload_to=get_chapter_upload_directory)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chapters")

    def __str__(self):
        return f'{self.course.title}/{self.title}'


class ChapterVideo(models.Model):
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=150)
    video = models.FileField(upload_to=get_video_upload_directory)

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='videos')

    def __str__(self):
        return f'{self.chapter.course.title}/{self.chapter.title}/{self.title}'
