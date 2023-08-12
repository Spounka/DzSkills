from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

UserModel = get_user_model()


# Create your models here.
class Notification(models.Model):
    REGISTER = 'register'
    COURSE_BUY = 'buy'

    PAYMENT_APPROVED = 'approve_payment'
    PAYMENT_REJECTED = 'reject_payment'

    COURSE_APPROVED = 'approve_course'
    COURSE_REJECTED = 'reject_course'

    # NOTIFICATION_CHOICES = (
    #     (REGISTER, _("New User Registered")),
    #     (COURSE_BUY, _("A User bought your course")),
    #
    #     (PAYMENT_APPROVED, _("Your payment has been approved")),
    #     (PAYMENT_REJECTED, _("Your payment has been rejected")),
    #
    #     (COURSE_APPROVED, _("Your course has been approved")),
    #     (COURSE_REJECTED, _("Your course has been rejected")),
    # )

    sender = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, related_name='sender_notifications')
    recipient = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True,
                                  related_name='recipient_notifications')
    notification_type = models.CharField(default='', max_length=35)
    is_read = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    extra_data = models.JSONField(null=True, blank=True)
