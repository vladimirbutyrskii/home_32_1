from django.contrib import admin
from lms.models import Course, Lesson
from lms.models import Subscription


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "course")
    list_filter = ("course",)
    search_fields = ("name",)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "course", "created_at")
    list_filter = ("course", "created_at")
    search_fields = ("user__email", "course__name")
    readonly_fields = ("created_at",)
