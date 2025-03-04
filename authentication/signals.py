from django.apps import AppConfig
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.db.models.signals import post_migrate, pre_save, post_save
from django.dispatch import receiver

from authentication.models import User


@receiver(post_migrate)
def create_permission_groups(sender: AppConfig, **kwargs: dict) -> None:
    if sender.name == "authentication":
        group_names = ['AdminGroup', 'TeacherGroup', 'StudentGroup']
        for group in group_names:
            try:
                Group.objects.get_or_create(name=group)
            except (Group.DoesNotExist, IntegrityError) as e:  # type Exception
                print(f'Creating {group} raised an error {e}')


@receiver(post_save, sender=User)
def add_new_user_to_student_group(sender, instance: User, created, **kwargs: dict) -> None:
    if created:
        student_group = Group.objects.get(name="StudentGroup")
        instance.groups.add(student_group)
