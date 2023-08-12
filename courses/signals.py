from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from . import models

UserModel = get_user_model()


@receiver(post_save, sender=models.Rating)
def update_chapter_average_rating(sender, instance: models.Rating, **kwargs):
    chapter = instance.video.chapter
    chapter.update_average_rating()
    chapter.save()


@receiver(post_delete, sender=models.Rating)
def update_chapter_average_rating_delete(sender, instance: models.Rating, **kwargs):
    chapter = instance.video.chapter
    chapter.update_average_rating()
    chapter.save()


@receiver(post_save, sender=models.Chapter)
def update_course_average_rating(sender, instance: models.Chapter, **kwargs):
    course = instance.course
    course.update_average_rating()
    course.save()


@receiver(post_delete, sender=models.Chapter)
def update_course_average_rating_delete(sender, instance: models.Chapter, **kwargs):
    course = instance.course
    course.update_average_rating()
    course.save()


@receiver(post_save, sender=models.Course)
def update_user_average_rating(sender, instance: models.Course, **kwargs):
    user = instance.owner
    user.update_average_rating()
    user.save()


@receiver(post_delete, sender=models.Course)
def update_user_average_rating_delete(sender, instance: models.Course, **kwargs):
    user = instance.owner
    user.update_average_rating()
    user.save()
