from rest_framework import generics, mixins, permissions, status, response
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from . import serializers, models
import courses.models


# Create your views here.
class GetCommentsFromVideo(generics.ListCreateAPIView):
    serializer_class = serializers.CommentSerializer
    queryset = models.Comment.objects.filter()

    def list(self, request, *args, **kwargs):
        video = get_object_or_404(courses.models.Video.objects.filter(), pk=kwargs.get('pk', None))
        serializer = self.get_serializer(video.comment_set, many=True)
        return response.Response(data=serializer.data, status=status.HTTP_200_OK)


class CreateComment(generics.CreateAPIView):
    serializer_class = serializers.CommentCreationSerializer
    queryset = models.Comment.objects.filter()
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {
            'request': self.request
        }


class UpdateDeleteComment(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.CommentSerializer
    queryset = models.Comment.objects.filter()
