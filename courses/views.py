from rest_framework import generics, response, mixins, status
from rest_framework.permissions import IsAuthenticated

from authentication.models import User
from authentication.serializers import UserSerializer
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
        # if (course := self.get_queryset().filter(pk=self.kwargs.get('pk'))) is not None:
        #     # course.app
        #     pass
        return super().partial_update(request, *args, **kwargs)

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


class StudentProgressAPI(generics.RetrieveAPIView, mixins.ListModelMixin):
    serializer_class = app.StudentProgressSerializer

    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        query = m.StudentProgress.objects.filter()
        filt = {'course': self.kwargs.get('pk'), 'user': request.user}
        obj = query.filter(**filt).get()
        serializer = self.get_serializer_class()
        data = serializer(obj)
        return response.Response(data=data.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        if not kwargs.get('pk'):
            return self.list(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)


class UpdateProgressAPI(generics.UpdateAPIView):
    queryset = m.StudentProgress.objects.filter()
    serializer_class = app.StudentProgressSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        progression = self.get_queryset().all()
        progression = progression.filter(user=self.request.user, course=self.kwargs.get('pk')).get()
        index_of_last_video = progression.course.chapters.all()[progression.last_chapter_index].videos.count() - 1

        index_of_last_chapter = progression.course.chapters.count() - 1
        if progression.last_video_index < index_of_last_video:
            progression.last_video_index += 1
        elif progression.last_chapter_index < index_of_last_chapter:
            progression.last_video_index = 0
            progression.last_chapter_index += 1
        else:
            progression.finished = True
        progression.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class GetCourseStudents(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = m.Course.objects.filter()

    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()
        serializer = self.get_serializer(course.user_set.all(), many=True)
        return response.Response(serializer.data)
