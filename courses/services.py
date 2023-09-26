import json

from django.contrib.auth import get_user_model

from . import models, serializers

UserModel = get_user_model()


class CourseService:
    @classmethod
    def create(cls, request, validated_data):
        models.Course.objects.filter(status=models.Course.REFUSED).delete()
        chapters_data = validated_data.pop('chapters', None)
        owner = request.user
        if owner.is_admin() and not owner.is_superuser:
            owner = UserModel.get_site_admin()
            validated_data['state'] = models.Course.RUNNING
            validated_data['status'] = models.Course.ACCEPTED

        course = models.Course.objects.create(owner=owner, **validated_data)
        quizz_data = request.data.get('quizz')

        if quizz_data:
            data = json.loads(quizz_data)
            data['course'] = course.pk
            serializer = serializers.CourseQuizzSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        chapters = []

        def update_video(video):
            set_video_duration(video)
            video.save()

        for chapter_data in chapters_data:
            videos_data = chapter_data.pop('videos')
            chapter = models.Chapter.objects.create(
                course=course, **chapter_data)
            videos = [models.Video.objects.create(
                chapter=chapter, **video_data) for video_data in videos_data]
            from courses.models import set_video_duration
            map(lambda video: update_video(video), videos)

            chapter.videos.set(videos)
            chapters.append(chapter)

        course.chapters.set(chapters)

        hashtags = []
        hashtags_data = None
        hashtags_str = request.data.get('hashtags')
        if hashtags_str:
            hashtags_data = json.loads(hashtags_str)
        if hashtags_data:
            for hashtag_data in hashtags_data.get('objs'):
                data = serializers.HashtagSerializer(data=hashtag_data)
                data.is_valid(raise_exception=True)
                del hashtag_data['courses']
                hashtags.append(models.Hashtag.objects.get(**hashtag_data))
        if hashtags:
            course.hashtags.set(hashtags)
        if (level := request.data.pop('course_level', None)) is not None:
            course.course_level = models.Level.objects.get(pk=level[0])
        if (category := request.data.pop('category', None)) is not None:
            course.category = models.Category.objects.get(pk=category[0])
        course.save()
        return course

    @classmethod
    def update(cls, instance: models.Course, request, validated_data: dict):
        models.Course.objects.filter(status=models.Course.REFUSED).delete()
        chapters = validated_data.pop('chapters', None)
        quizz_data = request.data.get('quizz', None)

        for chapter_data in chapters:
            videos_data = chapter_data.pop('videos', [])
            chap_pk = chapter_data.pop('id', 0)
            if chap_pk > 0:
                chap = models.Chapter.objects.get(pk=chap_pk)
                for field, value in chapter_data.items():
                    setattr(chap, field, value)
                chap.save()
            else:
                chap = models.Chapter.objects.create(course=instance, **chapter_data)

            for video in videos_data:
                if (pk := video.pop('id', 0)) > 0:
                    vid = models.Video.objects.get(pk=pk)
                    for field, value in video.items():
                        setattr(vid, field, value)
                    vid.save()
                else:
                    models.Video.objects.create(
                        chapter=chap, **video)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if quizz_data:
            if instance.quizz:
                json_data = json.loads(quizz_data)
                instance.quizz.update_self(json_data)
            else:
                data = json.loads(quizz_data)
                data['course'] = instance.pk
                serializer = serializers.CourseQuizzSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        hashtags = []
        hashtags_data = None
        hashtags_str = request.data.get('hashtags')
        if hashtags_str:
            hashtags_data = json.loads(hashtags_str)
        if hashtags_data:
            for hashtag_data in hashtags_data.get('objs'):
                data = serializers.HashtagSerializer(data=hashtag_data)
                data.is_valid(raise_exception=True)
                del hashtag_data['courses']
                hashtags.append(models.Hashtag.objects.get(**hashtag_data))

        if hashtags:
            instance.hashtags.set(hashtags)
        if level := request.data.get('course_level', None):
            instance.course_level = models.Level.objects.get(pk=level[0])
        if category := request.data.get('category', None):
            instance.category = models.Category.objects.get(pk=category[0])
        instance.status = instance.PENDING
        instance.save()
        return instance


class QuizzService:
    @classmethod
    def create(cls, course, questions):
        quizz = models.CourseQuizz.objects.create(course=course)
        questions_array = []
        for q in questions:
            answers_data = q.pop('choices')
            question = models.QuizzQuestion.objects.create(quizz=quizz, **q)
            choices = [models.QuizzChoice.objects.create(question=question, **a) for a in answers_data]
            question.choices.set(choices)
            question.save()
            questions_array.append(question)

        quizz.questions.set(questions_array)

        return quizz
