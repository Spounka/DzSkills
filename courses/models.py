from django.conf import settings
from django.contrib.auth import get_user_model
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


class Hashtag(models.Model):
    name = models.CharField(max_length=10, default="")


class Category(models.Model):
    name = models.CharField(max_length=30, default="")


class Level(models.Model):
    name = models.CharField(max_length=30, default="")


class Course(models.Model):
    PENDING = 'pend'
    ACCEPTED = 'app'
    REFUSED = 'rej'

    BEGINNER = 'beg'
    INTERMEDIATE = 'interm'
    ADVANCED = 'advanced'

    STATUS_CHOICES = [
        (PENDING, _("Pending")),
        (ACCEPTED, _("Approved")),
        (REFUSED, _("Rejected")),
    ]

    LEVEL_CHOICES = [
        (BEGINNER, _("Beginner")),
        (INTERMEDIATE, _("Intermediate")),
        (ADVANCED, _("Advanced")),
    ]

    title = models.CharField(max_length=300)
    description = models.CharField(max_length=300)
    thumbnail = models.ImageField(upload_to=get_course_image_upload_directory)
    price = models.PositiveIntegerField()
    hashtags = models.CharField(max_length=100)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=PENDING)
    trending = models.BooleanField(default=False)
    presentation_file = models.FileField(upload_to=get_course_file_upload_directory, blank=True, null=True)

    course_level = models.CharField(max_length=30, choices=LEVEL_CHOICES, default=BEGINNER)
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True)
    duration = models.CharField(max_length=10, default="1h")
    used_programs = models.CharField(max_length=300, default="")
    language = models.CharField(max_length=30, default="Arabic")

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses")

    def approve(self):
        self.status = self.ACCEPTED
        self.save()

    def reject(self):
        self.status = self.REFUSED
        self.save()

    @property
    def videos_count(self):
        videos = 0
        for chapter in self.chapters.all():
            videos += chapter.videos.count()
        return videos

    def __str__(self):
        return self.title


class Chapter(models.Model):
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=300)
    thumbnail = models.ImageField(upload_to=get_chapter_upload_directory)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chapters")

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f'{self.course.title}/{self.title}'


def get_duration(video: 'Video'):
    from moviepy.video.io.VideoFileClip import VideoFileClip

    clip = VideoFileClip(video.video.path)
    duration_seconds = int(clip.duration)
    duration_minutes, duration_seconds = divmod(duration_seconds, 60)
    duration_hours, duration_minutes = divmod(duration_minutes, 60)
    clip.close()
    return f'{duration_hours:02}:{duration_minutes:02}:{duration_seconds:02}'


def set_video_duration(video: 'Video'):
    video.duration = get_duration(video)


def set_videos_duration():
    for course in Course.objects.all():
        for chapter in course.chapters.all():
            for video in chapter.videos.all():
                if video.duration == "":
                    continue
                set_video_duration(video)


class Video(models.Model):
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=150)
    video = models.FileField(upload_to=get_video_upload_directory)
    duration = models.CharField(default="", blank=True, max_length=10)

    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='videos')

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f'{self.chapter.course.title}/{self.chapter.title}/{self.title}'


UserModel = get_user_model()


class StudentProgress(models.Model):
    user: UserModel = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    course: Course = models.ForeignKey(Course, on_delete=models.CASCADE)

    last_video_index = models.SmallIntegerField(default=0)
    last_chapter_index = models.SmallIntegerField(default=0)
    progress_percentage = models.FloatField(default=0.0)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return f'StudentProgress {self.user.username} - {self.course.title}'
