import json

from django.http import QueryDict
from rest_framework import generics, response, mixins, permissions, status
from rest_framework.permissions import IsAuthenticated

from . import serializers as app, models as m


# Create your views here.
class VideoAPI(generics.RetrieveUpdateAPIView):
    serializer_class = app.VideoSerializer
    queryset = m.Video.objects.filter()


class VideoListAPI(generics.ListAPIView):
    serializer_class = app.VideoSerializer
    queryset = m.Video.objects.filter()


class ChapterAPI(generics.ListCreateAPIView):
    serializer_class = app.ChapterSerializer

    def get_queryset(self):
        return m.Course.objects.filter(pk=self.kwargs.get('pk')).first().chapters.all()

    def create(self, request, *args, **kwargs):
        data = request.data
        data['course'] = kwargs['pk']
        serializer = app.CourseChapterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CourseAPI(generics.ListCreateAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    serializer_class = app.CourseSerializer
    queryset = m.Course.objects.filter()

    # permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('pk', None):
            return self.retrieve(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not self.kwargs.get('pk', None):
            return response.Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'no course provided'})
        if (course := self.get_queryset().filter(pk=self.kwargs.get('pk'))) is not None:
            # course.app
            pass

    def create(self, request, *args, **kwargs):
        chapters = request.data.get('chapters')
        data = request.data.copy()
        data["chapters"] = chapters

        serializer = app.CourseSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TrendingCourses(generics.ListAPIView):
    serializer_class = app.CourseSerializer
    queryset = m.Course.objects.filter(trending=True)
