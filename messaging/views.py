import zipfile

from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q, OuterRef, Subquery
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework import generics, pagination, permissions, decorators
from django.utils.translation import gettext_lazy as _
from authentication.models import User

import courses.models
from . import models, serializers

UserModel = get_user_model()
COURSE_OWNERSHIP_ERROR = _("You Don't Own This Course!")


# Create your views here.
class MessagePagination(pagination.CursorPagination):
    page_size = 25
    ordering = '-date'
    cursor_query_param = 'c'


class MessagesListAPIView(generics.ListAPIView):
    serializer_class = serializers.MessageSerializer
    pagination_class = MessagePagination
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        conversation = models.Conversation.objects.filter(
            pk=self.kwargs['pk']).first()
        return conversation.messages.all()


class MessagesCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.MessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = models.Message.objects.all()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ConversationsListAPIView(generics.ListAPIView):
    serializer_class = serializers.ConversationsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        latest_date_subquery = models.Message.objects.filter(conversation=OuterRef('pk')).order_by('-date').values(
            'date')[:1]
        if self.request.user.is_admin():
            user = User.get_site_admin()
        else:
            user = self.request.user
        conversations = models.Conversation.objects.filter(
            Q(recipient=user) | Q(student=user))
        if not user.is_admin():
            conversations = conversations.filter(Q(course__state=courses.models.Course.RUNNING,
                                                   course__status=courses.models.Course.ACCEPTED) |
                                                 Q(ticket__isnull=False))
        return conversations.annotate(last_date=Subquery(latest_date_subquery)).order_by('-last_date',
                                                                                         'ticket__date').all()


class TeacherConversationsListAPIView(generics.ListAPIView):
    serializer_class = serializers.ConversationsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        latest_date_subquery = models.Message.objects.filter(conversation=OuterRef('pk')).order_by('-date').values(
            'date')[:1]
        user = self.request.user
        if user.is_admin() or user.is_superuser:
            user = user.get_site_admin()
        conversations = models.Conversation.objects.filter(
            Q(recipient=user, ticket__isnull=True) | Q(student=user, ticket__isnull=True))
        return conversations.annotate(last_date=Subquery(latest_date_subquery)).order_by('-last_date',
                                                                                         'ticket__date').all()


class GetTeacherStudentConversationAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.ConversationsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def check_permissions(self, request: WSGIRequest):
        super().check_permissions(request)
        course = courses.models.Course.objects.get(pk=self.kwargs.get('pk'))
        if User.get_site_admin().pk == course.owner.pk and request.user.is_admin():
            return
        if not request.user.owns_course(course_id=self.kwargs.get('pk')):
            self.permission_denied(request, message=COURSE_OWNERSHIP_ERROR)

    def get_object(self):
        return self.get_queryset().first()

    def get_queryset(self):
        student = self.request.user
        course = courses.models.Course.objects.get(pk=self.kwargs.get('pk'))
        conversation = models.Conversation.objects.filter(
            Q(student=student, course=course) | Q(
                recipient=student, course=course)
        )
        query = conversation.all()
        return query


@decorators.permission_classes([permissions.IsAuthenticated])
def download_message_files(_, pk, *__, **___):
    message = models.Message.objects.get(pk=pk)
    files = message.files.all()

    if len(files) > 0:
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=file.zip'

        with zipfile.ZipFile(response, 'w') as zipfiles:
            for file in files:
                zipfiles.writestr(file.file.name.split('/')
                                  [-1], file.file.read())
        response['Content-Length'] = response.tell()
        return response
    return HttpResponseBadRequest(_('No Files for this message'))
