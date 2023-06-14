from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

import authentication.serializers
from . import models as models

UserModel = get_user_model()


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rating
        fields = ['id', 'rating', 'student', 'video']
        depth = 0
        extra_kwargs = {
            'video': {'write_only': True},
        }


class VideoSerializer(serializers.ModelSerializer):
    ratings = RatingSerializer(many=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = models.Video
        fields = "__all__"
        depth = 0

    def get_average_rating(self, video: models.Video):
        return video.get_average_rating()


class ChapterVideoSerializer(serializers.ModelSerializer):
    ratings = RatingSerializer(many=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = models.Video
        fields = ['id', 'title', 'description', 'video', 'duration', 'ratings', 'average_rating']
        read_only_fields = ('average_rating',)

    def get_average_rating(self, video: models.Video):
        return video.get_average_rating()


class CourseChapterSerializer(serializers.ModelSerializer):
    videos = ChapterVideoSerializer(many=True)

    class Meta:
        model = models.Chapter
        depth = 0
        fields = ['id', 'title', 'description', 'thumbnail', 'videos', 'average_rating']
        read_only_fields = ('average_rating',)

    def create(self, validated_data: dict[str, Any]):
        videos_data = validated_data.pop('videos', None)
        chapter = models.Chapter.objects.create(**validated_data)
        videos = [models.Video.objects.create(chapter=chapter, **data) for data in videos_data]
        chapter.videos.set(videos)
        return chapter


class CourseSerializer(serializers.ModelSerializer):
    chapters = CourseChapterSerializer(many=True)
    owner = authentication.serializers.UserSerializer(read_only=True)
    videos_count = serializers.ReadOnlyField()

    def create(self, validated_data):
        chapters_data = validated_data.pop('chapters', None)
        owner = self.context['request'].user
        course = models.Course.objects.create(owner=owner, **validated_data)
        chapters = []
        for chapter_data in chapters_data:
            videos_data = chapter_data.pop('videos')
            chapter = models.Chapter.objects.create(course=course, **chapter_data)
            videos = [models.Video.objects.create(chapter=chapter, **video_data) for video_data in videos_data]
            from courses.models import set_video_duration

            def update_video(video):
                set_video_duration(video)
                video.save()

            map(lambda video: update_video(video), videos)

            chapter.videos.set(videos)
            chapters.append(chapter)
        course.chapters.set(chapters)
        return course

    class Meta:
        model = models.Course
        fields = "__all__"
        read_only_fields = ('average_rating',)
        depth = 2


class ChapterSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Chapter
        depth = 2
        fields = ['pk', 'title', 'description', 'thumbnail', 'videos', 'average_rating']
        read_only_fields = ('average_rating',)


class StudentProgressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=models.Course.objects.filter())

    class Meta:
        model = models.StudentProgress
        fields = ('pk', 'last_chapter_index', 'last_video_index', 'user', 'course')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class StudentProgressForRelatedStudents(serializers.ModelSerializer):
    user = authentication.serializers.UserSerializer()

    # course = CourseSerializer()

    class Meta:
        model = models.StudentProgress
        fields = ['user', 'last_video_index', 'last_chapter_index', ]


class HashtagSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)

    class Meta:
        fields = ['id', 'name', 'courses']
        depth = 0
        model = models.Hashtag


class CreateHashtagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name']
        depth = 0
        model = models.Hashtag


class CategorySerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)

    class Meta:
        fields = "__all__"
        depth = 1
        model = models.Category


class LevelSerializer(serializers.ModelSerializer):
    courses = CourseSerializer(many=True)

    class Meta:
        fields = "__all__"
        depth = 1
        model = models.Level


class CreateLevelSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'name']
        depth = 0
        model = models.Level


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        depth = 0
        model = models.Certificate


class QuizzAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        depth = 0
        # fields = "__all__"
        exclude = ('question',)
        model = models.QuizzAnswer


class QuizzQuestionSerializer(serializers.ModelSerializer):
    answers = QuizzAnswerSerializer(many=True)

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
            answers_data = q.pop('answers')
            question = models.QuizzQuestion.objects.create(quizz=quizz, **q)
            answers = [models.QuizzAnswer.objects.create(question=question, **q) for a in answers_data]

            question.answers.set(answers)
            questions.append(question)

        quizz.questions.set(questions)

        return quizz

    class Meta:
        fields = "__all__"
        depth = 0
        model = models.CourseQuizz
