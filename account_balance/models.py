from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class AccountBalance(models.Model):
    user = models.OneToOneField('authentication.User', on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(default=0)


def min_money_request_validator(value):
    if value < 1000:
        raise ValidationError(
            _(f"{value} cannot be lower than 1000"),
            params={"value": value}
        )


class MoneyRequest(models.Model):
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PENDING = 'pending'
    STATUS_CHOICES = (
        (APPROVED, _("Approved")),
        (PENDING, _("Pending")),
        (REJECTED, _("Rejected")),
    )
    account = models.ForeignKey(AccountBalance, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=1000, validators=[min_money_request_validator])
    status = models.CharField(choices=STATUS_CHOICES, default=PENDING, max_length=25)
    date = models.DateTimeField(auto_now=True)
