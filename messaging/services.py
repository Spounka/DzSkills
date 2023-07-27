from django.core.exceptions import ValidationError
from django.db.models import Q

from django.utils.translation import gettext_lazy as _
from authentication.models import User
from courses.models import Course
from support.models import Ticket
from . import models


class ConversationService:
    @classmethod
    def get_or_create(cls, student: User, recipient: User, course: Course = None,
                      ticket: Ticket = None) -> models.Conversation:
        if not ((course is None) ^ (ticket is None)):
            raise ValueError('Must provide a course or a ticket to the create method of ConversationService')
        conversation = models.Conversation.objects.filter(Q(student=student, recipient=recipient))
        if course:
            conversation = conversation.filter(course=course).first()
        elif ticket:
            conversation = conversation.filter(ticket=ticket).first()

        if not conversation:
            conversation = models.Conversation.objects.create(student=student, recipient=recipient)
            if course:
                conversation.course = course
                conversation.save()
        return conversation


class MessageService:
    @classmethod
    def create(cls, sender: User, recipient: User, content: str, admin: User = None,
               course: Course = None, ticket: Ticket = None, files=None):
        if sender.is_admin():
            sender = User.get_site_admin()
        if course:
            owner = course.owner
            student = sender if course.owner.pk != sender.pk else recipient
        elif admin:
            owner = admin
            student = sender if admin.pk != sender.pk else recipient
        elif ticket:
            if ticket.state == ticket.CLOSED:
                raise ValidationError(_("Ticket Closed"))
            owner = User.get_site_admin()
            student = sender if User.get_site_admin().pk != sender.pk else recipient
        else:
            raise ValueError('Admin, Course and ticket are all None, aborting')

        conversation = ConversationService.get_or_create(
            student=student,
            recipient=owner,
            course=course,
            ticket=ticket
        )

        message = models.Message.objects.create(
            content=content,
            conversation=conversation,
            sender=sender,
            recipient=recipient
        )
        if files:
            message_files = [models.MessageFile(message=message, file=file) for file in files]
            models.MessageFile.objects.bulk_create(message_files, batch_size=15)

        return message
