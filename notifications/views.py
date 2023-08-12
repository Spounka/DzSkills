from django.shortcuts import render
from rest_framework import status, generics, permissions, response, pagination
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from . import models, serializers


class NotificationPagniator(pagination.CursorPagination):
    page_size = 5
    ordering = '-date_created'
    cursor_query_param = 'c'


# Create your views here.
class NotificationsAPIView(generics.ListAPIView):
    queryset = models.Notification.objects.all().prefetch_related('sender', 'recipient')
    serializer_class = serializers.NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_admin() or self.request.user.is_superuser:
            return queryset.filter(recipient=self.request.user.get_site_admin())
        return queryset.filter(recipient=self.request.user)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notifications_as_read(request, *args, **kwargs):
    if request.user.is_admin() or request.user.is_superuser:
        notifications = models.Notification.objects.filter(recipient=request.user.get_site_admin(), is_read=False)
    else:
        notifications = models.Notification.objects.filter(recipient=request.user, is_read=False)
    notifications.update(is_read=True)
    return response.Response(status=status.HTTP_204_NO_CONTENT)
