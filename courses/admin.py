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


class ChapterInline(admin.TabularInline):
    model = models.Chapter
    extra = 1


class LevelInline(admin.TabularInline):
    model = models.Chapter
    extra = 1


class CategoryInline(admin.TabularInline):
    model = models.Chapter
    extra = 1


class CourseInline(admin.TabularInline):
    model = models.Course
    extra = 1


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [
        CourseInline,
    ]


class CourseAdmin(admin.ModelAdmin):
    inlines = [
        ChapterInline,
        CategoryInline,
        LevelInline,
    ]


admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Chapter, ChapterAdmin)
admin.site.register(models.Video, VideoAdmin)
admin.site.register(models.Rating, admin.ModelAdmin)
admin.site.register(models.Hashtag, admin.ModelAdmin)
admin.site.register(models.Level, admin.ModelAdmin)
admin.site.register(models.StudentProgress, admin.ModelAdmin)
admin.site.register(models.Certificate, admin.ModelAdmin)
admin.site.register(models.QuizzQuestion, admin.ModelAdmin)
admin.site.register(models.QuizzAnswer, admin.ModelAdmin)
admin.site.register(models.CourseQuizz, admin.ModelAdmin)
