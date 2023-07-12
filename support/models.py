from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.
UserModel = get_user_model()


class Ticket(models.Model):
    OPEN = 'o'
    CLOSED = 'c'
    STATES = (
        (OPEN, _('Open')),
        (CLOSED, _('Closed')),
    )
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    state = models.CharField(choices=STATES, default=OPEN, max_length=30)
    date = models.DateTimeField(default=timezone.now)


class Report(models.Model):
    REPORT_REASONS = (
        ('tech', _('Technical Issues')),
        ('help', _('Help')),
        ('report', _('Report')),
    )

    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    reporter = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='ticket_reporter')
    reported = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='ticket_reported',
                                 verbose_name=_('Reported User'))
    report_date = models.DateTimeField(default=timezone.now, verbose_name=_('Report Date'))
    report_reason = models.TextField(max_length=30, choices=REPORT_REASONS, default='tech',
                                     verbose_name=_("Report Type"))
    report_description = models.TextField(max_length=3000, default="", verbose_name=_("Report Reason"))


class Conversation(models.Model):
    reporter = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='support_conversation')
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)

    def __str__(self):
        return f'conversation {self.reporter.username}'


class Message(models.Model):
    content = models.TextField(default="", max_length=300)
    date = models.DateTimeField(default=timezone.now)

    conversation = models.ForeignKey(Conversation, related_name="support_messages", on_delete=models.CASCADE)
    sender = models.ForeignKey('authentication.User', related_name="support_sender_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey('authentication.User', related_name="support_recipient_messages",
                                  on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.conversation} message {self.pk}'


def message_file_upload_folder(instance: 'MessageFile', filename: str):
    return f'messages/{instance.message.sender.username}/{instance.message.conversation.course.title}/{filename}'


class MessageFile(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to=message_file_upload_folder)

    def generate(self, message, paths):
        path, filename = paths
        self.message = message
        self.file.save(name=filename, content=open(path, 'rb'))
        self.save()
        return self

    def __str__(self):
        return f'{self.message.sender.username} - {self.file.name} file'
