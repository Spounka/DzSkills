from django.contrib.auth import get_user_model

from . import models

UserModel = get_user_model()


class CourseService:
    @classmethod
    def create(cls, owner: UserModel = None, chapters: list[models.Chapter] = None):
        chapters_data = validated_data.pop('chapters', None)
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
