from django.contrib import admin

from . import models


# Register your models here.
class VideoInline(admin.StackedInline):
    model = models.Video
    extra = 1


class RatingInline(admin.StackedInline):
    model = models.Rating


class VideoAdmin(admin.ModelAdmin):
    inlines = [
        RatingInline
    ]


class ChapterAdmin(admin.ModelAdmin):
    inlines = [
        VideoInline
    ]


class ChapterInline(admin.StackedInline):
    model = models.Chapter
    extra = 0


class LevelInline(admin.TabularInline):
    model = models.Chapter


class CategoryInline(admin.TabularInline):
    model = models.Chapter


class CourseInline(admin.TabularInline):
    model = models.Course


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        CourseInline,
    ]


class QuizzChoiceInline(admin.StackedInline):
    model = models.QuizzChoice


class QuizzQuestionAdmin(admin.ModelAdmin):
    inlines = [
        QuizzChoiceInline
    ]


class QuizzQuestionInline(admin.StackedInline):
    model = models.QuizzQuestion


class QuizzInline(admin.StackedInline):
    model = models.CourseQuizz


class QuizzAdmin(admin.ModelAdmin):
    inlines = [
        QuizzQuestionInline
    ]


class CourseAdmin(admin.ModelAdmin):
    inlines = [
        ChapterInline,
        CategoryInline,
        LevelInline,
        QuizzInline,
    ]


admin.site.register(models.Chapter, ChapterAdmin)
admin.site.register(models.Video, VideoAdmin)
admin.site.register(models.Rating, admin.ModelAdmin)
admin.site.register(models.Hashtag, admin.ModelAdmin)
admin.site.register(models.Level, admin.ModelAdmin)
admin.site.register(models.StudentProgress, admin.ModelAdmin)
admin.site.register(models.Certificate, admin.ModelAdmin)
admin.site.register(models.QuizzQuestion, QuizzQuestionAdmin)
admin.site.register(models.QuizzChoice, admin.ModelAdmin)
admin.site.register(models.CourseQuizz, QuizzAdmin)
admin.site.register(models.CourseEditRequest, admin.ModelAdmin)
admin.site.register(models.Course, CourseAdmin)
