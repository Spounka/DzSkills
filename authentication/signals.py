from django.apps import AppConfig
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_permission_groups(sender: AppConfig, **kwargs: dict) -> None:
    if sender.name == "authentication":
        group_names = ['AdminGroup', 'TeacherGroup', 'StudentGroup']
        for group in group_names:
            try:
                Group.objects.get_or_create(name=group)
            except (Group.DoesNotExist, IntegrityError) as e:  # type Exception
                e: Exception = e
                print(f'Creating {group} raised an error {e}')
