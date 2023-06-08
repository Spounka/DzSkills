from django.db.models import Q
from django.shortcuts import render
from rest_framework import viewsets, generics, pagination, permissions
from rest_framework.permissions import IsAuthenticated

import courses.models
from authentication.permissions import IsAdmin
from . import models, serializers
from .permissions import IsOwnerOrReadonly


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
    serializer_class = serializers.MessageSerializer
    pagination_class = MessagePagination
    permission_classes = [IsAuthenticated, ]
    queryset = models.Message.objects.all()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ConversationsListAPIView(generics.ListAPIView):
    serializer_class = serializers.ConversationsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return models.Conversation.objects.filter(Q(teacher=self.request.user) | Q(student=self.request.user)).all()


class GetTeacherStudentConversationAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.ConversationsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.get_queryset().first()

    def get_queryset(self):
        student = self.request.user
        course = courses.models.Course.objects.get(pk=self.kwargs.get('pk'))
        conversation = models.Conversation.objects.filter(student=student, course=course)
        query = conversation.all()
        return query
