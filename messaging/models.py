import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

# Create your models here.
UserModel = get_user_model()


class Conversation(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(UserModel, related_name="conversation_student", on_delete=models.CASCADE)
    recipient = models.ForeignKey(UserModel, related_name="conversation_recipient", on_delete=models.CASCADE)

    def __str__(self):
        if self.course:
            return f'{self.course.title} {self.student.username} {self.recipient.username} conversation'
        elif hasattr(self, 'ticket') and self.ticket:
            return f'Ticket Conversation {self.student.username} {self.ticket.date}'
        return 'Null Conversation'


class Message(models.Model):
    content = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(UserModel, related_name="sender_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(UserModel, related_name="recipient_messages", on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.conversation} message {self.pk}'


def message_file_upload_folder(instance: 'MessageFile', filename: str):
    if instance.message.conversation.course:
        return f'messages/{instance.message.sender.username}/{instance.message.conversation.course.title}/{filename}'
    return f'messages/{instance.message.sender.username}/{instance.message.conversation.ticket.__str__()}/{filename}'


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
