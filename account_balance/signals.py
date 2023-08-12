from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models
from authentication.models import User


@receiver(post_save, sender=User)
def on_new_teacher_create_balance(sender, instance: User, created, **kwargs):
    if instance.is_teacher():
        models.AccountBalance.objects.get_or_create(user=instance)


@receiver(post_save, sender=models.MoneyRequest)
def on_approve_money_request(sender, instance: models.MoneyRequest, created, **kwargs):
    if created:
        return
    if instance.status == instance.APPROVED:
        instance.account.balance -= instance.amount
        instance.account.save()
