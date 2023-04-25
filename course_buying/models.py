from django.db import models
from django.utils.translation import gettext_lazy as _

from authentication import models as auth
from django.utils import timezone


# Create your models here.
class Order(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    buyer = models.ForeignKey(auth.User, on_delete=models.CASCADE)
    date_issued = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Order {self.pk} {self.buyer.username}-{self.course.title}'


def get_payment_upload_path(instance: 'Payment', filename):
    return f'orders/{instance.order.buyer.username}/{instance.order.course.title}/payements/{filename}'


class Payment(models.Model):
    PENDING = 'p'
    ACCEPTED = 'a'
    REFUSED = 'r'

    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (ACCEPTED, _('Accepted')),
        (REFUSED, _('Refused')),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    receipt = models.FileField(upload_to=get_payment_upload_path)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=PENDING)

    def __str__(self):
        return f'{self.order.__str__()} Payment'
