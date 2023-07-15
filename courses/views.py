from django.db.models import Count
from rest_framework import generics, response, mixins, status, pagination
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from authentication.models import User
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


class CoursePagination(pagination.CursorPagination):
    page_size = 30
    ordering = '-average_rating'
    cursor_query_param = 'c'


class CourseAPI(generics.ListCreateAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin):
    serializer_class = app.CourseSerializer
    queryset = m.Course.objects.filter().prefetch_related('hashtags', 'course_level', 'category')

    def get_serializer_class(self):
        if self.kwargs.get('pk', None):
            return app.CourseSerializer
        return app.CourseListSerializer

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

    def check_permissions(self, request):
        super().check_permissions(request)
        if not request.user.is_superuser and not request.user.owns_course(course_id=self.kwargs.get('pk')):
            self.permission_denied(request, message="You don't have access")

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
        if progression.finished:
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        if progression.last_video_index < index_of_last_video:
            progression.last_video_index += 1
        elif progression.last_chapter_index < index_of_last_chapter:
            progression.last_video_index = 0
            progression.last_chapter_index += 1
        else:
            progression.finished = True
            certificate = m.Certificate()
            certificate.generate(request.user, progression.course)
        progression.save()
        return response.Response(status=status.HTTP_200_OK)


class GetCourseStudents(generics.RetrieveAPIView):
    serializer_class = app.StudentProgressForRelatedStudents
    queryset = m.Course.objects.filter()

    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()
        serializer = self.get_serializer_class()(course.studentprogress_set.all(), many=True)
        return response.Response(serializer.data)


class GetRelatedCourses(generics.RetrieveAPIView):
    serializer_class = app.CourseSerializer
    queryset = User.objects.filter()

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        courses_serialized = self.get_serializer_class()(user.courses.all(), many=True)
        return response.Response(courses_serialized.data)


class GetHashtagsAPI(generics.ListCreateAPIView):
    serializer_class = app.HashtagSerializer
    queryset = m.Hashtag.objects.all()

    def create(self, request, *args, **kwargs):
        self.serializer_class = app.CreateHashtagSerializer
        return super().create(request, *args, **kwargs)


class GetLevelsAPI(generics.ListCreateAPIView):
    serializer_class = app.LevelSerializer
    queryset = m.Level.objects.all()

    def create(self, request, *args, **kwargs):
        self.serializer_class = app.CreateLevelSerializer
        return super().create(request, *args, **kwargs)


class GetCategoryAPI(generics.ListCreateAPIView):
    serializer_class = app.CategorySerializer
    queryset = m.Category.objects.annotate(course_count=Count('courses')).order_by('-course_count')


class GetCertificate(generics.RetrieveAPIView):
    serializer_class = app.CourseSerializer
    queryset = m.Course.objects.filter()
    permission_classes = [IsAuthenticated, ]

    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()
        progress = m.StudentProgress.objects.filter(user=request.user, course=course)
        if progress.exists():
            certificate = m.Certificate.objects.filter(user=request.user).filter(course=course)
            if not certificate.exists():
                certificate = m.Certificate()
                certificate.generate(request.user, course)
            serializer = app.CertificateSerializer(certificate.first())
            return response.Response(data=serializer.data, status=status.HTTP_200_OK)
        return response.Response(status=status.HTTP_403_FORBIDDEN)


class ListCreateRatings(generics.ListCreateAPIView, mixins.UpdateModelMixin):
    serializer_class = app.RatingSerializer
    queryset = m.Rating.objects.all()
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        video = m.Video.objects.get(pk=self.kwargs.get('pk'))
        ratings = video.ratings.all()
        serializer = self.get_serializer(ratings, many=True)
        return response.Response(data=serializer.data, status=status.HTTP_200_OK)

    def get_object(self):
        video = m.Video.objects.filter(pk=self.kwargs.get('pk')).first()
        query = m.Rating.objects.filter(video=video, student=self.request.user)
        return query.first()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class QuizzRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView, mixins.CreateModelMixin):
    serializer_class = app.CourseQuizzSerializer
    queryset = m.CourseQuizz.objects.all()

    def get_object(self):
        lookup_field = self.lookup_url_kwarg or self.lookup_field
        return m.CourseQuizz.objects.filter(course_id=self.kwargs[lookup_field]).first()

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CourseStatusUpdateAPI(generics.UpdateAPIView):
    queryset = m.Course.objects.all()
    serializer_class = app.CourseSerializer

    def put(self, request, *args, **kwargs):
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        course: m.Course = self.get_object()
        serializer = self.get_serializer(course)
        course_status = kwargs.get('status', None)
        if course_status == 'approve' or course_status == 'accept':
            course.approve()
        elif course_status == 'reject' or course_status == 'refuse':
            course.reject()
        elif course_status == 'edit' or course_status == 'revisit':
            course.revise()
        else:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        return response.Response(status=status.HTTP_200_OK, data=serializer.data)
