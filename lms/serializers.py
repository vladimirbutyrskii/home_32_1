from rest_framework import serializers
from lms.models import Course, Lesson
from lms.validators import validate_youtube_link


class LessonSerializer(serializers.ModelSerializer):
    link_video = serializers.URLField(
        validators=[validate_youtube_link],
        required=False,
        allow_blank=True,
        allow_null=True
    )

    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ("owner",)


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.IntegerField(source="lessons.count", read_only=True)
    lessons = LessonSerializer(source="lessons", many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "pk",
            "name",
            "preview",
            "description",
            "lessons_count",
            "lessons",
            "owner",
        ]
        read_only_fields = ("owner",)

    def validate_description(self, value):
        """
        Проверка описания курса на наличие запрещенных ссылок
        """
        if value:
            youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/'
            # Простая проверка: ищем любые URL в тексте
            import re
            urls = re.findall(r'https?://[^\s]+', value)
            for url in urls:
                if not re.match(youtube_pattern, url):
                    raise serializers.ValidationError(
                        "В описании курса обнаружена ссылка на сторонний ресурс. "
                        "Разрешены только ссылки на youtube.com."
                    )
        return value