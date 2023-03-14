import json

from django.http import QueryDict
from rest_framework import generics, response, mixins, permissions, status
from rest_framework.permissions import IsAuthenticated

from . import serializers as app, models as m


# Create your views here.
class VideoAPI(generics.RetrieveUpdateAPIView):
    serializer_class = app.VideoSerializer
    queryset = m.ChapterVideo.objects.filter()


class VideoListAPI(generics.ListAPIView):
    serializer_class = app.VideoSerializer
    queryset = m.ChapterVideo.objects.filter()


class ChapterAPI(generics.ListCreateAPIView):
    serializer_class = app.ChapterSerializer
    queryset = m.Chapter.objects.filter()

    def create(self, request, *args, **kwargs):
        data = request.data
        data['course'] = kwargs['pk']
        serializer = app.CourseChapterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CourseAPI(generics.ListCreateAPIView):
    serializer_class = app.CourseSerializer
    queryset = m.Course.objects.filter()
    # permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        chapters = request.data.get('chapters')
        data = request.data.copy()
        data["chapters"] = chapters

        serializer = app.CourseSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
