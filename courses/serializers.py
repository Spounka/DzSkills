import json
from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

import authentication.serializers
import courses.models
from . import models as models
from .services import CourseService

UserModel = get_user_model()


class LevelSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()

    class Meta:
        fields = "__all__"
        depth = 0
        model = models.Level

    def get_courses(self, hashtag):
        return hashtag.courses.count()


class CategorySerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = "__all__"
        depth = 0
        model = models.Category

    def get_courses(self, hashtag):
        return hashtag.courses.count()

    def update(self, instance, validated_data):
        validated_data['image'] = validated_data.get('image') or instance.image
        return super().update(instance, validated_data)


class HashtagSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()

    class Meta:
        fields = ['id', 'name', 'courses']
        depth = 0
        model = models.Hashtag

    def get_courses(self, hashtag):
        return hashtag.courses.count()


class QuizzChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        depth = 0
        exclude = ('question',)
        model = models.QuizzChoice


class QuizzQuestionSerializer(serializers.ModelSerializer):
    choices = QuizzChoiceSerializer(many=True)

    class Meta:
        exclude = ('quizz',)
        depth = 0
        model = models.QuizzQuestion


class CourseQuizzSerializer(serializers.ModelSerializer):
    questions = QuizzQuestionSerializer(many=True)

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', None)
        quizz = models.CourseQuizz.objects.create(**validated_data)
        questions = []
        for q in questions_data:
            answers_data = q.pop('choices')
            question = models.QuizzQuestion.objects.create(quizz=quizz, **q)
            choices = [models.QuizzChoice.objects.create(
                question=question, **a) for a in answers_data]

            question.choices.set(choices)
            question.save()
            questions.append(question)

        quizz.questions.set(questions)

        return quizz

    class Meta:
        fields = "__all__"
        depth = 0
        model = models.CourseQuizz


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rating
        fields = ['id', 'rating', 'student', 'video']
        depth = 0
        extra_kwargs = {
            'video': {'write_only': True},
        }


class VideoSerializer(serializers.ModelSerializer):
    ratings = RatingSerializer(many=True, read_only=True, required=False)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = models.Video
        fields = ['id', 'title', 'description', 'video', 'thumbnail', 'presentation_file', 'duration', 'ratings',
                  'average_rating']
        depth = 0

    def get_average_rating(self, video: models.Video):
        return video.get_average_rating()


class ChapterVideoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    ratings = RatingSerializer(many=True, required=False)
    average_rating = serializers.SerializerMethodField()
    video = serializers.FileField(required=False)

    class Meta:
        model = models.Video
        fields = ['id', 'title', 'description', 'video', 'thumbnail', 'presentation_file', 'duration', 'ratings',
                  'average_rating']
        read_only_fields = ('average_rating', 'ratings')

    def get_average_rating(self, video: models.Video):
        return video.get_average_rating()


class CourseChapterSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    videos = ChapterVideoSerializer(many=True, required=False)

    class Meta:
        model = models.Chapter
        depth = 0
        fields = ['id', 'title', 'description', 'videos', 'average_rating']
        read_only_fields = ('average_rating',)

    def create(self, validated_data: dict[str, Any]):
        videos_data = validated_data.pop('videos', None)
        chapter = models.Chapter.objects.create(**validated_data)
        videos = [models.Video.objects.create(
            chapter=chapter, **data) for data in videos_data]
        chapter.videos.set(videos)
        return chapter


class CourseSerializer(serializers.ModelSerializer):
    chapters = CourseChapterSerializer(many=True)
    owner = authentication.serializers.UserSerializer(read_only=True)
    videos_count = serializers.ReadOnlyField(required=False)
    hashtags = HashtagSerializer(many=True, required=False)
    course_level = LevelSerializer(required=False)
    category = CategorySerializer(required=False)
    quizz = CourseQuizzSerializer(required=False)
    thumbnail = serializers.ImageField(required=False)
    students_count = serializers.SerializerMethodField()

    def create(self, validated_data):
        return CourseService.create(self.context['request'], validated_data)

    def update(self, instance, validated_data):
        return CourseService.update(instance, self.context['request'], validated_data)

    class Meta:
        model = models.Course
        fields = "__all__"
        read_only_fields = ('average_rating',)
        depth = 2

    def get_students_count(self, instance: models.Course):
        return models.StudentProgress.objects.filter(course=instance, disabled=False).count()


class CourseListSerializer(serializers.ModelSerializer):
    owner = authentication.serializers.UserSerializer(read_only=True)
    videos_count = serializers.ReadOnlyField()
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = "__all__"
        read_only_fields = ('average_rating',)
        depth = 2

    def get_students_count(self, instance: models.Course):
        return models.StudentProgress.objects.filter(course=instance, disabled=False).count()


class ChapterSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Chapter
        depth = 2
        fields = ['pk', 'title', 'description', 'videos', 'average_rating']
        read_only_fields = ('average_rating',)


class StudentProgressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    course = serializers.PrimaryKeyRelatedField(
        queryset=models.Course.objects.filter())
    percentage = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.StudentProgress
        fields = ('pk', 'last_chapter_index', 'last_video_index',
                  'finished', 'user', 'course', 'percentage')

    def get_percentage(self, instance: models.StudentProgress):
        if instance.finished:
            return 100
        chapters = instance.course.chapters.all()[:instance.last_chapter_index]
        watched_videos = sum([chapter.videos.count() for chapter in chapters])
        watched_videos += instance.last_video_index
        return round(watched_videos / instance.course.videos_count * 100, 2)


class StudentProgressForRelatedStudents(serializers.ModelSerializer):
    user = authentication.serializers.UserSerializer()

    class Meta:
        model = models.StudentProgress
        fields = ['user', 'last_video_index', 'last_chapter_index', ]
        depth = 2


class CreateHashtagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name']
        depth = 0
        model = models.Hashtag


class CreateLevelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name']
        depth = 0
        model = models.Level


class CertificateSerializer(serializers.ModelSerializer):
    certificate_image = serializers.ImageField()

    class Meta:
        fields = ['id', 'user', 'course', 'certificate_image']
        depth = 1
        model = models.Certificate


class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        depth = 0
        model = models.StudentAnswer


class StudentAttemptSerializer(serializers.ModelSerializer):
    answers = serializers.PrimaryKeyRelatedField(many=True, queryset=models.StudentAnswer.objects.all(),
                                                 source='answers')
    student = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = "__all__"
        depth = 1


class StudentProgressCourseDeleteSerializer(serializers.Serializer):
    students = serializers.ListSerializer(
        child=serializers.IntegerField(), required=True)


class HashtagsDeleteSerializer(serializers.Serializer):
    hashtags = serializers.ListSerializer(
        child=serializers.IntegerField(), required=True)


class LevelsDeleteSerializer(serializers.Serializer):
    levels = serializers.ListSerializer(
        child=serializers.IntegerField(), required=True)


class CategoriesDeleteSerializer(serializers.Serializer):
    categories = serializers.ListSerializer(
        child=serializers.IntegerField(), required=True)


class EditReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseEditRequest
        fields = "__all__"
