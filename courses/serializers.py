from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers

import authentication.serializers
from . import models as main

UserModel = get_user_model()


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = main.ChapterVideo
        fields = "__all__"
        depth = 0


class ChapterVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = main.ChapterVideo
        fields = ['title', 'description', 'video']


class CourseChapterSerializer(serializers.ModelSerializer):
    videos = ChapterVideoSerializer(many=True)

    class Meta:
        model = main.Chapter
        depth = 0
        fields = ['title', 'description', 'thumbnail', 'videos']

    def create(self, validated_data: dict[str, Any]):
        videos_data = validated_data.pop('videos', None)
        chapter = main.Chapter.objects.create(**validated_data)
        videos = [main.ChapterVideo.objects.create(chapter=chapter, **data) for data in videos_data]
        chapter.videos.set(videos)
        return chapter


class CourseSerializer(serializers.ModelSerializer):
    chapters = CourseChapterSerializer(many=True)
    owner = authentication.serializers.UserDetails(read_only=True)

    def serialize(self):
        return

    def create(self, validated_data):
        chapters_data = validated_data.pop('chapters', None)
        owner = self.context['request'].user if not self.context[
            'request'].user.is_anonymous else UserModel.objects.all().first()
        course = main.Course.objects.create(owner=owner, **validated_data)
        chapters = []
        for chapter_data in chapters_data:
            videos_data = chapter_data.pop('videos')
            chapter = main.Chapter.objects.create(course=course, **chapter_data)
            videos = [main.ChapterVideo.objects.create(chapter=chapter, **video_data) for video_data in videos_data]
            chapter.videos.set(videos)
            chapters.append(chapter)
        chapters = [main.Chapter.objects.create(course=course, **data) for data in chapters_data]
        course.chapters.set(chapters)
        return course

    class Meta:
        model = main.Course
        fields = ['pk', 'title', 'description', 'thumbnail', 'price', 'owner', 'chapters', 'presentation_file']
        depth = 2


class ChapterSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)
    course = CourseSerializer()

    class Meta:
        model = main.Chapter
        depth = 2
        fields = ['pk', 'title', 'description', 'thumbnail', 'videos', 'course']
