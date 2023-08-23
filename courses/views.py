from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, mixins, status, pagination, permissions
from rest_framework.decorators import api_view, permission_classes
from notifications.service import NotificationService

import course_buying.models
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
        return m.Course.objects.filter(pk=self.kwargs.get("pk")).first().chapters.all()

    def create(self, request, *args, **kwargs):
        data = request.data
        data["course"] = kwargs["pk"]
        serializer = app.CourseChapterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class CoursePagination(pagination.CursorPagination):
    page_size = 30
    ordering = "-average_rating"
    cursor_query_param = "c"


COURSE_BLOCKED_ERROR = _("This Course is either paused or blocked")


class CourseAPI(
    generics.ListCreateAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    serializer_class = app.CourseSerializer
    queryset = m.Course.objects.filter().prefetch_related(
        "hashtags", "course_level", "category"
    )

    def check_permissions(self, request):
        super().check_permissions(request)
        if not self.kwargs.get("pk"):
            return
        if self.request.user.is_authenticated and (
            self.request.user.is_superuser or self.request.user.is_admin()
        ):
            return
        course: m.Course = self.get_object()
        if course.status != course.ACCEPTED:
            self.permission_denied(request, _("You can't view this course"))
        if course.state != course.RUNNING:
            self.permission_denied(request, _("You can't view this course"))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_serializer_class(self):
        if self.kwargs.get("pk", None) or self.request.method not in ["GET", "OPTIONS"]:
            return app.CourseSerializer
        return app.CourseListSerializer

    # @method_decorator(cache_page(60 * 60 * 24, key_prefix='courses'))
    def get(self, request, *args, **kwargs):
        if self.kwargs.get("pk", None):
            return self.retrieve(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not self.kwargs.get("pk", None):
            return response.Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"message": "no course provided"},
            )
        # if (course := self.get_queryset().filter(pk=self.kwargs.get('pk'))) is not None:
        #     # course.app
        #     pass
        return super().partial_update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class TrendingCourses(generics.ListAPIView):
    serializer_class = app.CourseSerializer
    queryset = m.Course.objects.filter(trending=True, state="running", status="app")

    # @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class MostSoldCourses(generics.ListAPIView):
    serializer_class = app.CourseListSerializer
    queryset = m.Course.objects.annotate(
        students_count=Count("studentprogress")
    ).order_by("-students_count", "-average_rating")

    # @method_decorator(cache_page(60 * 60 * 24))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


COURSE_OWNERSHIP_ERROR = _("You Don't Own This Course!")


class CourseStateUpdate(generics.UpdateAPIView):
    serializer_class = app.CourseSerializer
    queryset = m.Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        course = self.get_object()
        if request.user.is_admin() or request.user.is_superuser:
            if request.user.owns_course(course_id=course.pk):
                course.state = (
                    course.PAUSED if course.state == course.RUNNING else course.RUNNING
                )
            else:
                course.state = (
                    course.BLOCKED if course.state == course.RUNNING else course.RUNNING
                )
                owner = course.owner
                if not (owner.is_admin() or owner.is_superuser):
                    NotificationService.create(
                        sender=User.get_site_admin(),
                        recipient_user=course.owner,
                        notification_type="course_blocked",
                        extra_data={
                            "course": app.CourseListSerializer(
                                course, context={"request": request}
                            ).data
                        },
                    )
            course.save()
            return response.Response(
                data=self.get_serializer(course, context={"request": request}).data,
                status=status.HTTP_200_OK,
            )
        elif request.user.owns_course(course_id=course.pk):
            course.state = (
                course.PAUSED if course.state == course.RUNNING else course.RUNNING
            )
            course.save()
            return response.Response(
                data=self.get_serializer(course, context={"request": request}).data,
                status=status.HTTP_200_OK,
            )
        return response.Response(
            status=status.HTTP_403_FORBIDDEN, data={"message": COURSE_OWNERSHIP_ERROR}
        )


class GetStudentCourses(generics.ListAPIView):
    serializer_class = app.CourseListSerializer
    queryset = m.Course.objects.all().prefetch_related("studentprogress_set")
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.kwargs.get("pk"):
            return self.queryset.filter(
                studentprogress__in=m.StudentProgress.objects.filter(
                    user_id=self.kwargs.get("pk"), disabled=False
                )
            )
        return self.queryset.filter(
            studentprogress__in=m.StudentProgress.objects.filter(
                user=self.request.user.pk, disabled=False
            )
        )

    # @method_decorator(vary_on_headers('Authorization'))
    # @method_decorator(cache_page(60 * 30))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class StudentProgressAPI(generics.RetrieveAPIView, mixins.ListModelMixin):
    serializer_class = app.StudentProgressSerializer

    permission_classes = [permissions.IsAuthenticated]

    def check_permissions(self, request):
        super().check_permissions(request)
        if not (
            request.user.is_superuser or request.user.is_admin()
        ) and not request.user.owns_course(course_id=self.kwargs.get("pk")):
            self.permission_denied(request, message="You don't have access")

    def retrieve(self, request, *args, **kwargs):
        query = m.StudentProgress.objects.filter(disabled=False)
        filt = {"course": self.kwargs.get("pk"), "user": request.user}
        try:
            obj = query.filter(**filt).get()
            serializer = self.get_serializer_class()
            data = serializer(obj)
            return response.Response(data=data.data, status=status.HTTP_200_OK)
        except m.StudentProgress.DoesNotExist:
            return response.Response(status=status.HTTP_403_FORBIDDEN)

    # @method_decorator(cache_page(60 * 30))
    def get(self, request, *args, **kwargs):
        if not kwargs.get("pk"):
            return self.list(request, *args, **kwargs)
        return self.retrieve(request, *args, **kwargs)


class UpdateProgressAPI(generics.UpdateAPIView):
    queryset = m.StudentProgress.objects.filter(disabled=False)
    serializer_class = app.StudentProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        progression = self.get_queryset().all()
        progression = progression.filter(
            user=self.request.user, course=self.kwargs.get("pk")
        ).get()
        index_of_last_video = (
            progression.course.chapters.all()[
                progression.last_chapter_index
            ].videos.count()
            - 1
        )

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
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # @method_decorator(cache_page(60 * 60 * 4))
    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()
        serializer = self.get_serializer_class()(
            course.studentprogress_set.all(), context={"request": request}, many=True
        )
        return response.Response(serializer.data)


class GetRelatedCourses(generics.RetrieveAPIView):
    serializer_class = app.CourseSerializer
    queryset = User.objects.filter()
    permission_classes = [permissions.IsAuthenticated]

    # @method_decorator(cache_page(60 * 60 * 4))
    # @method_decorator(vary_on_headers('Authorization'))
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_admin():
            courses = User.get_site_admin().courses.all()
        else:
            courses = user.courses.all()
        courses_serialized = self.get_serializer_class()(
            courses, many=True, context={"request": request}
        )
        return response.Response(courses_serialized.data)


class GetHashtagsAPI(generics.ListCreateAPIView):
    serializer_class = app.HashtagSerializer
    queryset = m.Hashtag.objects.all()

    # @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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
    queryset = m.Category.objects.annotate(course_count=Count("courses")).order_by(
        "-course_count"
    )

    # @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class EditDeleteHashtag(generics.UpdateAPIView, mixins.DestroyModelMixin):
    serializer_class = app.HashtagSerializer
    queryset = m.Hashtag.objects.all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class EditDeleteLevel(generics.UpdateAPIView, mixins.DestroyModelMixin):
    serializer_class = app.LevelSerializer
    queryset = m.Level.objects.all()

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class EditDeleteCategory(generics.UpdateAPIView, mixins.DestroyModelMixin):
    serializer_class = app.CategorySerializer
    queryset = m.Category.objects.all()

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class GetCertificate(generics.RetrieveAPIView):
    serializer_class = app.CertificateSerializer
    queryset = m.Course.objects.filter()
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        course = self.get_object()
        progress = m.StudentProgress.objects.filter(
            user=request.user, course=course, disabled=False
        )
        if progress.exists():
            certificate = m.Certificate.objects.filter(user=request.user).filter(
                course=course
            )
            if not certificate.exists():
                certificate = m.Certificate()
                certificate.generate(request.user, course)
                serializer = self.get_serializer(certificate)
            else:
                serializer = self.get_serializer(certificate.first())
            return response.Response(data=serializer.data, status=status.HTTP_200_OK)
        return response.Response(status=status.HTTP_403_FORBIDDEN)


class ListCreateRatings(
    generics.ListCreateAPIView, mixins.UpdateModelMixin, mixins.RetrieveModelMixin
):
    serializer_class = app.RatingSerializer
    queryset = m.Rating.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request, *args, **kwargs):
        video = m.Video.objects.get(pk=self.kwargs.get("pk"))
        ratings = video.ratings.all()
        serializer = self.get_serializer(ratings, many=True)
        return response.Response(data=serializer.data, status=status.HTTP_200_OK)

    def get_object(self):
        video = m.Video.objects.filter(pk=self.kwargs.get("pk")).first()
        query = m.Rating.objects.filter(video=video, student=self.request.user)
        return query.last()

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class QuizzRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView, mixins.CreateModelMixin
):
    serializer_class = app.CourseQuizzSerializer
    queryset = m.CourseQuizz.objects.all()

    def get_object(self):
        lookup_field = self.lookup_url_kwarg or self.lookup_field
        return m.CourseQuizz.objects.filter(course_id=self.kwargs[lookup_field]).first()

    # @method_decorator(cache_page(60 * 60 * 8))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CourseStatusUpdateAPI(generics.UpdateAPIView):
    queryset = m.Course.objects.all()
    serializer_class = app.CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        course: m.Course = self.get_object()
        serializer = self.get_serializer(course)
        course_status = kwargs.get("status", None)
        if course_status == "approve" or course_status == "accept":
            course.approve()
            NotificationService.create(
                sender=User.get_site_admin(),
                recipient_user=course.owner,
                notification_type="course_accepted",
                extra_data={
                    "course": app.CourseListSerializer(
                        course, context={"request": request}
                    ).data
                },
            )
        elif course_status == "reject" or course_status == "refuse":
            course.reject()
            NotificationService.create(
                sender=User.get_site_admin(),
                recipient_user=course.owner,
                notification_type="course_refused",
                extra_data={
                    "course": app.CourseListSerializer(
                        course, context={"request": request}
                    ).data
                },
            )
        elif course_status == "edit" or course_status == "revisit":
            course.revise()
        else:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        return response.Response(status=status.HTTP_200_OK, data=serializer.data)


class RemoveStudentsFromCourseAPI(generics.UpdateAPIView):
    serializer_class = app.StudentProgressCourseDeleteSerializer
    queryset = m.StudentProgress.objects.filter(disabled=False)

    def update(self, request, *args, **kwargs):
        try:
            course = m.Course.objects.get(pk=self.kwargs.get("pk"))
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            for student_id in serializer.validated_data.get("students"):
                try:
                    order = course_buying.models.Order.objects.filter(
                        buyer_id=student_id, course_id=course.pk
                    ).first()
                    order.payment.status = order.payment.REFUSED
                    order.payment.save()
                    order.save()
                    progression = m.StudentProgress.objects.filter(
                        course=course.pk, user_id=student_id
                    )
                    progression.delete()
                    NotificationService.create(
                        sender=User.get_site_admin(),
                        recipient_user=order.buyer,
                        notification_type="removed_from_course",
                        extra_data={
                            "course": app.CourseListSerializer(
                                course, context={"request": request}
                            ).data
                        },
                    )
                    return response.Response(status=status.HTTP_200_OK)
                except (
                    m.StudentProgress.DoesNotExist,
                    course_buying.models.Order.DoesNotExist,
                ):
                    continue

        except m.Course.DoesNotExist:
            return response.Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"message": _("Couse does not exist")},
            )
        return response.Response(
            status=status.HTTP_404_NOT_FOUND,
            data={"message": _("Couse does not exist")},
        )


class HashtagsDelete(generics.UpdateAPIView):
    serializer_class = app.HashtagsDeleteSerializer
    queryset = m.Hashtag.objects.filter()
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for pk in serializer.validated_data.get("hashtags"):
            try:
                hashtag = self.queryset.get(pk=pk)
                hashtag.delete()
            except m.Hashtag.DoesNotExist:
                continue
        return response.Response(status=status.HTTP_200_OK)


class LevelsDelete(generics.UpdateAPIView):
    serializer_class = app.LevelsDeleteSerializer
    queryset = m.Level.objects.filter()
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for pk in serializer.validated_data.get("levels"):
            try:
                level = self.queryset.get(pk=pk)
                level.delete()
            except m.Level.DoesNotExist:
                continue
        return response.Response(status=status.HTTP_200_OK)


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def make_course_favourite(request, *args, **kwargs):
    try:
        course = m.Course.objects.get(pk=kwargs.get("pk", None))
        course.trending = not course.trending
        course.save()
        NotificationService.create(
            sender=User.get_site_admin(),
            recipient_user=course.owner,
            notification_type="course_favourite",
            extra_data={
                "course": app.CourseListSerializer(
                    course, context={"request": request}
                ).data
            },
        )
        return response.Response(
            status=status.HTTP_200_OK, data=app.CourseSerializer(course).data
        )
    except m.Course.DoesNotExist:
        return response.Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"code": "not_found", "message": _("Course not found")},
        )
