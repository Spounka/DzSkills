import zipfile

from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from rest_framework import generics, pagination, permissions
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _

import courses.models
from . import models, serializers

UserModel = get_user_model()
COURSE_OWNERSHIP_ERROR = _("You Don't Own This Course!")


# Create your views here.
class MessagePagination(pagination.CursorPagination):
    page_size = 20
    ordering = '-date'
    cursor_query_param = 'c'


class MessagesListAPIView(generics.ListAPIView):
    serializer_class = serializers.MessageSerializer
    pagination_class = MessagePagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation = models.Conversation.objects.get(pk=self.kwargs['pk'])
        return conversation.messages.all()


class MessagesCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.MessageCreateSerializer
    permission_classes = [IsAuthenticated, ]
    queryset = models.Message.objects.all()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ConversationsListAPIView(generics.ListAPIView):
    serializer_class = serializers.ConversationsSerializer
    permission_classes = [IsAuthenticated]

    def check_permissions(self, request: HttpRequest):
        super().check_permissions(request)
        if not request.user.owns_course(course_id=self.kwargs.get('pk')):
            self.permission_denied(request, message=COURSE_OWNERSHIP_ERROR)

    def get_queryset(self):
        return models.Conversation.objects.filter(Q(teacher=self.request.user) | Q(student=self.request.user)).all()


class GetTeacherStudentConversationAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.ConversationsSerializer
    permission_classes = [IsAuthenticated]

    def check_permissions(self, request: WSGIRequest):
        super().check_permissions(request)
        if not request.user.owns_course(course_id=self.kwargs.get('pk')):
            self.permission_denied(request, message=COURSE_OWNERSHIP_ERROR)

    def get_object(self):
        return self.get_queryset().first()

    def get_queryset(self):
        student = self.request.user
        course = courses.models.Course.objects.get(pk=self.kwargs.get('pk'))
        conversation = models.Conversation.objects.filter(student=student, course=course)
        query = conversation.all()
        return query


def download_message_files(_, pk, *__, **___):
    message = models.Message.objects.get(pk=pk)
    files = message.files.all()

    if len(files) > 0:
        response = HttpResponse(content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=file.zip'

        with zipfile.ZipFile(response, 'w') as zipfiles:
            for file in files:
                zipfiles.writestr(file.file.name.split('/')[-1], file.file.read())
        response['Content-Length'] = response.tell()
        return response
    return HttpResponseBadRequest(_('No Files for this message'))
