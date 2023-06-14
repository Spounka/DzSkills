from django.db.models import Q

from authentication.models import User
from courses.models import Course
from . import models


class MessageService:
    @classmethod
    def create(cls, sender: User, recipient: User, content: str, course: Course, files=None):
        conversation = models.Conversation.objects.filter(
            Q(student=sender, teacher=recipient) | Q(teacher=sender, student=recipient)).filter(course=course).first()
        teacher = course.owner
        student = sender if course.owner.pk != sender.pk else recipient
        if not conversation:
            conversation = models.Conversation.objects.create(
                course=course,
                student=student,
                teacher=teacher
            )
        message = models.Message.objects.create(
            content=content,
            conversation=conversation,
            sender=sender,
            recipient=recipient
        )
        if files:
            message_files = [models.MessageFile(message=message, file=file) for file in files]
            models.MessageFile.objects.bulk_create(message_files)

        return message
