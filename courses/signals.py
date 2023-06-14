from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import models

UserModel = get_user_model()


@receiver(post_save, sender=models.Video)
def update_chapter_average_rating(sender, instance: models.Video, **kwargs):
    chapter = instance.chapter
    chapter.update_average_rating()
    chapter.save()


@receiver(post_save, sender=models.Chapter)
def update_course_average_rating(sender, instance: models.Chapter, **kwargs):
    course = instance.course
    course.update_average_rating()
    course.save()


@receiver(post_save, sender=models.Course)
def update_user_average_rating(sender, instance: models.Course, **kwargs):
    user = instance.owner
    user.update_average_rating()
    user.save()
