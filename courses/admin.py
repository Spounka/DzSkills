from django.contrib import admin

from . import models


# Register your models here.
class VideoInline(admin.StackedInline):
    model = models.Video
    extra = 1


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


class CourseAdmin(admin.ModelAdmin):
    inlines = [
        ChapterInline,
        CategoryInline,
        LevelInline,
    ]


admin.site.register(models.Course, CourseAdmin)
admin.site.register(models.Chapter, ChapterAdmin)
admin.site.register(models.Video, admin.ModelAdmin)
admin.site.register(models.Hashtag, admin.ModelAdmin)
admin.site.register(models.Category, admin.ModelAdmin)
admin.site.register(models.Level, admin.ModelAdmin)
admin.site.register(models.StudentProgress, admin.ModelAdmin)
