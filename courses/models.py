from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.utils.translation import gettext_lazy as _

from certificate_generation.main import generate_certificate
from courses.upload_paths import get_course_image_upload_directory, get_course_file_upload_directory, \
    get_video_upload_directory, get_chapter_upload_directory, get_category_upload_dir, certificate_upload_dir

UserModel = get_user_model()


# Create your models here.
class Hashtag(models.Model):
    name = models.CharField(max_length=20, default="")

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=30, default="")
    description = models.CharField(max_length=300, default="")
    image = models.ImageField(upload_to=get_category_upload_dir, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Level(models.Model):
    name = models.CharField(max_length=30, default="")

    def __str__(self):
        return self.name


class Course(models.Model):
    PENDING = 'pend'
    ACCEPTED = 'app'
    REFUSED = 'rej'

    STATUS_CHOICES = [
        (PENDING, _("Pending")),
        (ACCEPTED, _("Approved")),
        (REFUSED, _("Rejected")),
    ]

    title = models.CharField(max_length=300)
    description = models.CharField(max_length=300)
    thumbnail = models.ImageField(upload_to=get_course_image_upload_directory)
    price = models.PositiveIntegerField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=PENDING)
    trending = models.BooleanField(default=False)
    presentation_file = models.FileField(upload_to=get_course_file_upload_directory, blank=True, null=True)

    course_level = models.ForeignKey(Level, blank=True, on_delete=models.SET_NULL, null=True,
                                     related_name="courses")
    category = models.ForeignKey(Category, blank=True, on_delete=models.SET_NULL, null=True, related_name="courses")
    hashtags = models.ManyToManyField(Hashtag, blank=True, related_name="courses")

    duration = models.CharField(max_length=10, default="1h")
    used_programs = models.CharField(max_length=300, default="")
    language = models.CharField(max_length=30, default="Arabic")
    average_rating = models.FloatField(default=0)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses")

    class Meta:
        ordering = ['-average_rating']

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

    def update_average_rating(self):
        ratings = [chapter.average_rating for chapter in self.chapters.all() if chapter.average_rating > 0]
        if len(ratings) > 0:
            average = sum(ratings) / len(ratings)
            self.average_rating = average

    def __str__(self):
        return self.title


class Chapter(models.Model):
    title = models.CharField(max_length=300)
    description = models.CharField(max_length=300)
    thumbnail = models.ImageField(upload_to=get_chapter_upload_directory)
    average_rating = models.FloatField(default=0)

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="chapters")

    def update_average_rating(self):
        ratings = [video.get_average_rating() for video in self.videos.all() if video.get_average_rating() > 0]
        if len(ratings) > 0:
            average = sum(ratings) / len(ratings)
            self.average_rating = average

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f'{self.course.title}/{self.title}'


class CourseQuizz(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='quizz')

    def __str__(self):
        return f'{self.course.title}-quizz'


class QuizzQuestion(models.Model):
    quizz = models.ForeignKey(CourseQuizz, on_delete=models.CASCADE, related_name="questions")
    content = models.CharField(max_length=200, default="")

    def __str__(self):
        return f'{self.quizz.course.title}-question {self.pk:02}'


class QuizzChoice(models.Model):
    question = models.ForeignKey(QuizzQuestion, on_delete=models.CASCADE, related_name="choices")
    content = models.CharField(max_length=200, default="")
    is_correct_answer = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.question.quizz.course.title}-question {self.question.pk:02} answer'


class StudentAttempt(models.Model):
    quizz = models.ForeignKey(CourseQuizz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='attempts')
    score = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-pk']


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(StudentAttempt, on_delete=models.CASCADE, related_name='answers')
    answer = models.ForeignKey(QuizzChoice, on_delete=models.CASCADE, related_name='answer')


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

    def get_average_rating(self):
        # value = cache.get(f'video_average_{self.pk}')
        # if not value:
        ratings = self.ratings.values_list('rating', flat=True)
        if len(ratings) > 0:
            value = sum(ratings) / len(ratings)
        else:
            value = 0
        # cache.set(f'video_average_{self.pk}', value)
        return value

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return f'{self.chapter.course.title}/{self.chapter.title}/{self.title}'


class StudentProgress(models.Model):
    user: UserModel = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    course: Course = models.ForeignKey(Course, on_delete=models.CASCADE)

    last_video_index = models.SmallIntegerField(default=0)
    last_chapter_index = models.SmallIntegerField(default=0)
    progress_percentage = models.FloatField(default=0.0)
    finished = models.BooleanField(default=False)

    def __str__(self):
        return f'StudentProgress {self.user.username} - {self.course.title}'


class Certificate(models.Model):
    user: UserModel = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    course: Course = models.ForeignKey(Course, on_delete=models.CASCADE)

    certificate_image = models.ImageField(upload_to=certificate_upload_dir)

    def generate(self, user, course):
        certificate_image = generate_certificate(f'{user.first_name} {user.last_name}')
        certificate_image.save(f'/tmp/certificate-{user.username}.png')
        self.user = user
        self.course = course
        self.certificate_image.save(name="certificate.png",
                                    content=open(f'/tmp/certificate-{user.username}.png', 'rb'),
                                    save=True)
        self.save()
        # os.remove(f'certificate-{user.username}.png')


class Rating(models.Model):
    student: UserModel = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    video: Video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name="ratings")

    rating = models.FloatField(default=0)
